# xtend_tuya
HomeAssistant eXtend Tuya's integration

# Current status
The custom component is working as expected

# Purpose
This Custom Integration is there to add the missing entities in Tuya's integration.<br/>
The reason why this is not merged in the main Tuya integration is that the way this is done is not officially supported by HomeAssistant (AKA this integration is using hacks to do its job)

# Installation
You have 2 choices to install, either via Home Assistant Community Store (HACS) or using manual install:<br/>
1- HACS (recommended)<br/>
Add the current repository URL to your HACS repositories by going into HACS, click the 3 dots, add custom repository.<br/>
In the screen, fill azerty9971/xtend_tuya as the repository, select integration as type and click add.<br/>
Now you can download xtend_tuya directly from HACS (and get notified when I update it)<br/>
<br/>
2- Manual installation (advanced)<br/>
Clone the repository and put all the files using SSH to your /homeassistant/custom_components folder (final folder will look like: /homeassistant/custom_components/xtend_tuya)<br/>
Once this is done, restart your HomeAssistant instance, go to Settings -> Devices and integrations -> Add integration -> type "Tuya" and select Xtended Tuya<br/>

# Usage
Once installed, the base devices should have the new entities automatically added and they should be supported in the Energy dashboard for instance<br/>
If you have more than 1 tuya account, click go to the Xtended Tuya configuration page (Settings -> Devices and integrations -> Xtended Tuya) and click "Add a bridge", this will pull the next available Tuya configuration available (repeat for more)

# Adding your Tuya Cloud credentials
If you have missing entities, you can try inserting your Tuya Cloud API credentials.
To do that, go to the Xtended Tuya integration page, next to your account, click the "configure" button.
You'll be prompted for cloud credentials, for an assistance on how to get these, follow the following tutorial:
https://www.youtube.com/watch?v=y6kNHIYcJ5c
Please watch out that the username is the same as the username displayed in the regular Tuya integration
(the gg-106053160716494114782 in the following screenshot)
![image](https://github.com/user-attachments/assets/8f8ec9d3-1454-4ef5-8871-61ab4c12de90)

