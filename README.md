# SquadSDKUtils
This repo contains scripts to help Squad SDK modders. These scripts run as python unreal script.
# How to use it
Clone the repo
Execute the desired script in the Squad SDK
Select your mod configuration file
Check the UE4 output log
# Scripts
## postCook
src/postCook.py

It removes the file "DevelopmentAssetRegistry.bin" from the cooked package.
Run it when your cook process succeed and before uploading your mod into the steam workshop.
The file is generated during the cook process but it's not used by the game. It help to reduce the size of your mod
## updateProjectInformation
src/updateProjectInformation.py
If you add folder in your mod conf in the "assetValidatorExcludeDirectories", it will rewrite the "DefaultEditor.ini" file to add the exclusion for your mod only
If you've set addVanillaOption it will add the vanilla option in the modified files.
It will update your asset manager setting depending of the value in "assetManager" in your mod conf file
It will update the "directories to never cook" option according of the value in "directoriesToNeverCook"
