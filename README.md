# Sample pyang plugin

## Invoking the plugin with pyang

Cd to the git repr root and execute below cmd
```
pyang --plugindir plugins -f my-plugin models/napalm-star-wars.yang
```

## Generating pybind for an yag model

```
export PYBINDPLUGIN=`/usr/bin/env python3 -c 'import pyangbind; import os; print ("{}/plugin".format(os.path.dirname(pyangbind.__file__)))'`
pyang --plugindir $PYBINDPLUGIN -f pybind models/napalm-star-wars.yang > napalm_star_wars.py
```

## References

- [yang-for-dummies](https://napalm-automation.net/yang-for-dummies/)
