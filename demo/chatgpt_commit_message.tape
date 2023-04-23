Output ../chatgpt-pre-commit-hooks/docs/assets/demos/chatgpt_commit_message.gif
Output ../chatgpt-pre-commit-hooks/demo/chatgpt_commit_message.ascii

Require figlet
#Require lolcrab
Require lolcat
Require git
Require pre-commit

Set Shell bash
Set Framerate 30
Set FontSize 20
Set Width 1200
Set Height 600
Set Padding 40
Set WindowBar Colorful

Hide
#Type@0 "pushd ../.vhs_demo_repo"
#Enter
Type@0 "PS1='\n\[\e[38;2;90;86;224m\]> \[\e[0m\]'"
Enter
Type@0 "clear && figlet -f demo/ogre.flf -w 88 '  > > >   ChatGPT   < < < commit message' | lolcat --seed=9 && echo"
Enter
Show
Sleep 500ms

Type "echo '# Hello World!' > HELLO_WORLD.md"
Enter
Sleep 1s

Type "cat HELLO_WORLD.md"
Enter
Sleep 1s

Type "git status -s"
Enter
Sleep 1s

Type "git add HELLO_WORLD.md"
Enter
Sleep 1s

Type "git status -s"
Enter
Sleep 1s

Type 'git commit -m "my test msg"'
Enter
Sleep 12s

Type 'git log -1 --pretty=format:%s%n%n%b'
Enter
Sleep 5s

Hide
Type@0 "rm -f HELLO_WORLD.md"
Enter
#Type@0 "popd"
#Enter
