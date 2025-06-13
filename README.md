> [!CAUTION]
> This is a purely EDUCATIONAL project, do not run it for the purpose of benefit.
> To note, I did not benefit in the creation of this program, I had these posts open in my normal browser already. I merely wished to experiment with Selenium :)
>
> I am not liable for any damages you cause with this.

# Roblox Devforum Automation
![image](https://gist.github.com/user-attachments/assets/a96c167a-e88a-43e6-a651-df6d527be667)

It will automatically log you in to devforums if you provide it proper cookies.

It will select the first 5 posts in Help and Feedback, reading every reply.

If you've already read replies, the script will skip them.

## Instructions:
### Cookie setup
Use a tool like [Cookie-Editor](https://cookie-editor.com/) to export your cookies as json.

You only need to export ROBLOSECURITY, but the script doesnt care if you export everything.

Copy your exported cookies into a cookies.json file in this directory.

> [!CAUTION]
> Do NOT share your ROBLOSECURITY cookies.
>
> Keep this file safe at all costs, or you can get hacked.

### Running script
Simply run `poetry run python main.py --continue`
Only run if you agree to the cautionary warning.
