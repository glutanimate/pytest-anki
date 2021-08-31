from copy import deepcopy

from aqt import gui_hooks
from aqt import mw


addon_manager = mw.addonManager
package_name = addon_manager.addonFromModule(__name__)
config = addon_manager.getConfig(package_name)

# Copy in case the values in question are mutable. We want to make
# sure to record the state at execution time.
meta_storage = deepcopy(mw.pm.meta.get(package_name))

profile_storage = None
colconf_storage = None

def on_profile_did_open():
    global colconf_storage
    global profile_storage
    colconf_storage = deepcopy(mw.col.get_config(package_name, default=None))
    profile_storage = deepcopy(mw.pm.profile.get(package_name))

gui_hooks.profile_did_open.append(on_profile_did_open)