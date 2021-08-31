## Specifications for sample add-ons

### Packed add-ons

.ankiaddon-packed add-ons should follow these specifications:

File name:

```
 <package_name>.ankiaddon
```

Package contents:

```
__init__.py
manifest.json
```

`__init__.py` contents:

```
from aqt import mw

mw.<package_name> = True

print("<package_name>")
```

`manifest.json` contents:

```
{
    "name": "<package_name>",
    "package": "<package_name>"
}
```


### Unpacked add-ons

Unpacked add-ons follow the same specifications as packed add-ons, with the difference that they are not packaged in an .ankiaddon file, but added in their unpacked form.

The unpacked folder should follow the following naming:

```
<package_name>
```

Its contents should be identical to the top-level contents of a packed add-on.