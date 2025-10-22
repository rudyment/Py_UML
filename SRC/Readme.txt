Soubor DrawUML.py zkopírujte do

%LOCALAPPDATA%\Programs\Python\%VERSION%\Lib\idlelib 

Do té samé složky zkopírujte celý adresář,
ve kterém je tento soubor obsažený (můžete z něj vynechat soubor DrawUML.py,
nicméně pokud ho v něm necháte, nic se neděje)

Následné je třeba přidat virtuální událost do souboru config-extensions.def,
který se nachází také v této složce
a je ho možné otevřít běžným textovým editorem.

Na konec souboru vložte následující text:

[DrawUML]
enable= True
enable_shell = False
enable_editor = True

[DrawUML_cfgBindings]
umlcreate= <Control-Key-y>

Pro spuštění nástroje slouží klávesové zkratka ctrl+y
nebo výběrem přes hlavní nabídku Options.
