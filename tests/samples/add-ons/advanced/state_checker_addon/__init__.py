from aqt import mw

addon_manager = mw.addonManager

package_name = addon_manager.addonFromModule(__name__)

config = addon_manager.getConfig(package_name)
