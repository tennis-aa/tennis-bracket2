import os
import json

def mergeBrackets(inFolder,outFolder=None):
    if outFolder is None:
        outFolder = inFolder
    try:
        with open(os.path.join(outFolder,"brackets.json"),"r", encoding="utf-8") as f:
            brackets = json.load(f)
    except:
        brackets = {}

    for filename in os.listdir(inFolder):
        if not filename.endswith(".json"):
            continue
        if filename in ["bots.json","brackets.json","config.json","monkeys.json","players.json","results.json"]:
            continue
        with open(os.path.join(inFolder,filename),"r", encoding="utf-8") as f:
            bracket = json.load(f)
            brackets.update(bracket)

    with open(os.path.join(outFolder,"brackets.json"),"w", encoding="utf-8") as f:
        f.write(json.dumps(brackets,sort_keys=True))

    return