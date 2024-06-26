[Setup]
AppName=YouTube Help
AppVersion=1.0
DefaultDirName={pf}\YouTube_Help
DefaultGroupName=ChickenWithACrown
OutputBaseFilename=YouTube Help

[Files]
Source: "dist\YouTube_Help.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\YouTube_Help"; Filename: "{app}\YouTube_Help.exe"
