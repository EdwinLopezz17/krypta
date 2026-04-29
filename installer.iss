[Setup]
AppName=Krypta
AppVersion=1.1.0
AppPublisher=Edwin
DefaultDirName={autopf}\Krypta
DefaultGroupName=Krypta
OutputBaseFilename=Krypta-Setup
OutputDir=release
Compression=lzma
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; \
  Description: "Crear acceso directo en el escritorio"; \
  GroupDescription: "Accesos directos:"; \
  Flags: unchecked

[Files]
; Ejecutable principal
Source: "dist\Krypta.exe"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
; Crear carpeta data dentro de Program Files con permisos de escritura
Name: "{app}\data"; Permissions: users-modify

[Icons]
Name: "{group}\Krypta";       Filename: "{app}\Krypta.exe"
Name: "{group}\Desinstalar";  Filename: "{uninstallexe}"
Name: "{userdesktop}\Krypta"; Filename: "{app}\Krypta.exe"; \
  Tasks: desktopicon

[Run]
Filename: "{app}\Krypta.exe"; \
  Description: "Iniciar Krypta ahora"; \
  Flags: nowait postinstall skipifsilent
  