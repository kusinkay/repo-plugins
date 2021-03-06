# coding=utf-8
# Gnu General Public License - see LICENSE.TXT

import xbmcgui
import xbmcplugin
import xbmc
import urllib
import httplib
import base64
import sys
import threading
import time

from downloadutils import DownloadUtils
from simple_logging import SimpleLogging
from json_rpc import json_rpc
from translation import i18n
from datamanager import DataManager
from utils import getArt, double_urlencode

downloadUtils = DownloadUtils()
log = SimpleLogging(__name__)


class CacheArtwork(threading.Thread):

    stop_all_activity = False

    def __init__(self):
        log.debug("CacheArtwork init")
        self.stop_all_activity = False
        super(CacheArtwork, self).__init__()

    def run(self):
        log.debug("CacheArtwork background thread started")
        last_update = 0
        while not self.stop_all_activity and not xbmc.abortRequested:
            if (time.time() - last_update) > 300:
                self.cache_artwork_background()
                last_update = time.time()

            xbmc.sleep(1000)
        log.debug("CacheArtwork background thread exited")

    def cache_artwork_interactive(self):
        log.debug("cache_artwork_interactive")

        xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=False)

        # is the web server enabled
        web_query = {"setting": "services.webserver"}
        result = json_rpc('Settings.GetSettingValue').execute(web_query)
        xbmc_webserver_enabled = result['result']['value']
        if not xbmc_webserver_enabled:
            xbmcgui.Dialog().ok(i18n('notice'), i18n('http_control'))
            return

        # ask to delete all textures
        question_result = xbmcgui.Dialog().yesno(i18n('delete'), i18n('delete_existing'))
        if question_result:
            pdialog = xbmcgui.DialogProgress()
            pdialog.create(i18n('deleting_textures'), "")
            index = 0

            json_result = json_rpc('Textures.GetTextures').execute()
            textures = json_result.get("result", {}).get("textures", [])
            log.debug("texture ids: {0}", textures)
            total = len(textures)
            for texture in textures:
                texture_id = texture["textureid"]
                params = {"textureid": int(texture_id)}
                json_rpc('Textures.RemoveTexture').execute(params)
                percentage = int((float(index) / float(total)) * 100)
                message = "%s of %s" % (index, total)
                pdialog.update(percentage, "%s" % (message))

                index += 1
                if pdialog.iscanceled():
                    break

            del textures
            del pdialog

        question_result = xbmcgui.Dialog().yesno(i18n('cache_all_textures_title'), i18n('cache_all_textures'))
        if not question_result:
            return

        pdialog = xbmcgui.DialogProgress()
        pdialog.create(i18n('caching_textures'), "")
        result_report = self.cache_artwork(pdialog)
        pdialog.close()
        del pdialog
        if result_report:
            xbmcgui.Dialog().ok(i18n('done'), "\n".join(result_report))

    def cache_artwork_background(self):
        log.debug("cache_artwork_background")
        dp = xbmcgui.DialogProgressBG()
        dp.create(i18n('caching_textures'), "")
        result_text = self.cache_artwork(dp)
        dp.close()
        del dp
        if result_text:
            log.debug("Cache Images reuslt : {0}", " - ".join(result_text))

    def cache_artwork(self, progress):
        log.debug("cache_artwork")

        # is the web server enabled
        web_query = {"setting": "services.webserver"}
        result = json_rpc('Settings.GetSettingValue').execute(web_query)
        xbmc_webserver_enabled = result['result']['value']
        if not xbmc_webserver_enabled:
            log.debug("Kodi web server not enabled, can not cache images")
            return

        # get the port
        web_port = {"setting": "services.webserverport"}
        result = json_rpc('Settings.GetSettingValue').execute(web_port)
        xbmc_port = result['result']['value']
        log.debug("xbmc_port: {0}", xbmc_port)

        # get the user
        web_user = {"setting": "services.webserverusername"}
        result = json_rpc('Settings.GetSettingValue').execute(web_user)
        xbmc_username = result['result']['value']
        log.debug("xbmc_username: {0}", xbmc_username)

        # get the password
        web_pass = {"setting": "services.webserverpassword"}
        result = json_rpc('Settings.GetSettingValue').execute(web_pass)
        xbmc_password = result['result']['value']

        params = {"properties": ["url"]}
        json_result = json_rpc('Textures.GetTextures').execute(params)
        textures = json_result.get("result", {}).get("textures", [])

        if self.stop_all_activity:
            return

        texture_urls = set()
        for texture in textures:
            url = texture.get("url")
            url = urllib.unquote(url)
            url = url.replace("image://", "")
            url = url[0:-1]
            texture_urls.add(url)

        del textures
        del json_result

        if self.stop_all_activity:
            return

        url = ('{server}/emby/Users/{userid}/Items?' +
            '&Recursive=true' +
            '&IncludeItemTypes=Movie,Series,Episode,BoxSet' +
            '&ImageTypeLimit=1' +
            '&format=json')

        data_manager = DataManager()
        results = data_manager.GetContent(url)
        if results is None:
            results = []

        if isinstance(results, dict):
            results = results.get("Items")

        server = downloadUtils.getServer()
        missing_texture_urls = set()

        if self.stop_all_activity:
            return

        image_types = ["thumb", "poster", "banner", "clearlogo", "tvshow.poster", "tvshow.banner", "tvshow.landscape"]
        for item in results:
            art = getArt(item, server)
            for image_type in art:
                image_url = art[image_type]
                if image_url not in texture_urls and not image_url.endswith("&Tag=") and len(image_url) > 0:
                    missing_texture_urls.add(image_url)

            if self.stop_all_activity:
                return

        log.debug("texture_urls: {0}", texture_urls)
        log.debug("missing_texture_urls: {0}", missing_texture_urls)
        log.debug("Number of existing textures: {0}", len(texture_urls))
        log.debug("Number of missing textures: {0}", len(missing_texture_urls))

        kodi_http_server = "localhost:" + str(xbmc_port)
        headers = {}
        if xbmc_password:
            auth = "%s:%s" % (xbmc_username, xbmc_password)
            headers = {'Authorization': 'Basic %s' % base64.b64encode(auth)}

        total = len(missing_texture_urls)
        index = 1

        count_done = 0
        for get_url in missing_texture_urls:
            log.debug("texture_url: {0}", get_url)
            url = double_urlencode(get_url)
            kodi_texture_url = ("/image/image://%s" % url)
            log.debug("kodi_texture_url: {0}", kodi_texture_url)

            percentage = int((float(index) / float(total)) * 100)
            message = "%s of %s" % (index, total)
            progress.update(percentage, "%s" % (message))

            conn = httplib.HTTPConnection(kodi_http_server, timeout=20)
            conn.request(method="GET", url=kodi_texture_url, headers=headers)
            data = conn.getresponse()
            if data.status == 200:
                count_done += 1
            log.debug("Get Image Result: {0}", data.status)

            index += 1
            if "iscanceled" in dir(progress) and progress.iscanceled():
                break

            if self.stop_all_activity:
                break

        result_report = []
        result_report.append(i18n('existing_textures') + str(len(texture_urls)))
        result_report.append(i18n('missing_textures') + str(len(missing_texture_urls)))
        result_report.append(i18n('loaded_textures') + str(count_done))
        return result_report







