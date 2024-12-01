# Study Buddy
This app turns textbook chapters into podcasts.

### Convert PDF to XML 

A PDF, which is an image file, is converted to xml by pdf2xml_plain.py

Run the script, you will be prompted for a file path and a desired file name, and an .xml file will be generated. 
 
#### Format XML 
The xml must then be edited by hand, unless you can discover an automation.

If document exceeds max tokens (which it will), add xml headers to indicate batch edges.


<.page number=1> "batch 1" <./page>

<.page number=2> "batch 2" <./page>
               
"." included for visibility, please delete in code!


This can be tedious, but when done correctly prevents sections from being truncated during batching, ensuring they are whole when passed to llm.

###  Generate Text Script

A podcast-like text script is generated from the .xml using tts_opeai.py.

The script will be generated in batches, there should be the same amount of batches as "pages" indicated in the xml.

Run the script, you will be prompted for a file path(use the .xml file you use generated) and a desired file name. 

A .txt file will be generated. 

### Generate Speech for Podcast

The text is converted to realistic speech using tts_openai.py.

Run the script, you will be prompted for a file path (use the .txt you just generated) and a desired file name. 

Mp3 files will be generated.
      

#### Splice Them in a DAW

The text is converted to voice in batches, but attempts to splice the resultant .mp3 using ffmpeg. 

Failing this, splice them together in your favorite DAW (i use ableton of course).


## To Do
   
###  Automate it

???
  
### Text Search
xml -> unstructured -> json -> openai vector embedding -> weaviate

This could perhaps be done with a forked Verba

https://github.com/weaviate/Verba
