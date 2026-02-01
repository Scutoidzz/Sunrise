# Memoirs of an imperfect hacker

[January 31, 2026]
### 8 PM 
- Started coding, is going without a hitch

### 8:05 PM
 - I've reached my first issue. My past dimming function is interfering. I am unable to continue
 - I will have to rewrite the touchscreen UI from scratch.


 ### 8:09 PM
 - Alas, I am using a youtube PiP to keep myself awake
 - It will waste time to re activate my ublock origin lite right now, so I will have to wait until my break at 10PM to do it.
 - I HATE THE BASE44 AD WITH A BURNING PASSION

 ### 8:18 PM
 - I almost created a card class using a variable, huge blunder 
 - A way better way to implement it is to create a function by the name of
- create_card(self, content)    

### 8:24 PM
- I've found a mistake from earlier:
- I accidentally left the touchscreen selectors as QRadioButtons
- This is actually an easy fix:
- Switch out the QRadioButton for a QPushButton
- Currently commenting out the code while it's being changed.

### 8:28 PM
- Finshed implementation, removing comments

### 8:33 PM
- I've finished the downloading function, but I realized I've forgotten to add a function at the end to verify the functions are there
- I want the user to have a fast UI, so I will  not add a redownload, and instead create a card prompting the user to finish the download
- Though this may not be feasible for offline setups, however, I seem to plan a lot for a user demograpic that just doesn't exist
- I will be back after a five minute break, shortening my break at 10PM to 10 minutes. as of 8:40

### 8:45 PM
- Break is over, continuing to code and think.
- So, I need a way to download undownloaded models. 
- I'm considering reserving a QThread and then streaming the download while the screen is dimmed.
- When the user clicks the screen, it will show a card with the current download status.
- If the user chooses to ignore the card and tries to use Sunrise's wake work, instead of the normal animation and transcription, it shows a disabled version of the animation (static and grayed out.).
- It will also be able to show the current model downloading status in the transcription location.


### 8:52 PM
- What I need to do is find out how to make a if path exists for the checks
- I'm going to start out using ```os.pathExists```

### 9:02 PM
- My computer restarted itself, and I lost my Train of thought. Let me catch myself up
- Okay, so ```os.PathExists``` did not throw any errors, however it did not use my debug print ("Path exists"). It just ended the program with a successful code.
- While looking through the VScode snippets, I found ```os.listdir```. I set it to the path and changed mt if statement to use if not equal to blank. I will have to test that

### 9:08 PM
- I had to do a quick google. After finding a stackoverflow article, I found out I should use ```os.path.isdir```
- I will also use ```os.path.join``` to join the paths.


### 9:17 PM
- I just spent 9 minutes debugging to find out that I had forgotten to call the code's function.
- Fixed by running verify_files()
- After running, I see that it does return true.

### 9:23 PM
- Alright, I'm onto the next hurdle:
- The issue is that I need to save the stats into config.json
- I think that I just need to create an array. Let me try that out.

### 9:38
- I'm having a lot of issues with git, so I've seeked out the help of Gemini
- 