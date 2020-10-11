# CSGO-statistics-python
Small Python script for obtaining csgo account stats.

## Usage
1. Obtain Steam API key
2. Make sure your profile settings are correct ("11 april Steam announced that they made a change to the profile privacy settings. They introduced a new privacy setting that made it possible to hide your game and playtime statistics, this setting is for every Steam user now automatically set to private.")
3. run
```bash
python3 csgo.py APIKEY PROFILENAME
```
APIKEY = [Steam API](https://steamcommunity.com/dev/apikey)  
PROFILENAME = https://steamcommunity.com/id/*THISVALUE*/  
## Optional arguments
specify up to 5 weapons for comparison
Weapons list:
```python
        """'deagle', 'glock', 'elite', 'fiveseven', 'awp', 'ak47'"""  
        """'aug', 'famas', 'g3sg1', 'p90', 'mac10', 'ump45',"""  
        """'xm1014', 'm249', 'hkp2000', 'p250', 'sg556', 'scar20'"""  
        """'ssg08', 'mp7', 'mp9', 'nova', 'negev', 'sawedoff'"""  
        """'bizon', 'tec9', 'mag7', 'm4a1', 'galilar', 'taser']""" 
```
### Example 
```bash
python csgo.py D5FEAE35149*****08390054F8BE5D elek*****na -W awp,negev,ak47
```
## Example output
![Example output](https://maciekmajek2.usermd.net/media/Figure_1.png)
