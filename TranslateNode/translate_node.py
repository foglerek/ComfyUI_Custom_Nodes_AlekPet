import json
from server import PromptServer
from aiohttp import web
from googletrans import Translator, LANGUAGES

### =====  Translate Nodes [googletrans module]  ===== ###
translator = Translator()

@PromptServer.instance.routes.post("/alekpet/translate_manual")
async def translate_manual(request):
    json_data =  await request.json()
    prompt = json_data.get("prompt", "")
    
    if "prompt" in json_data and "srcTrans" in json_data and "toTrans" in json_data:
        prompt = json_data.get("prompt")
        srcTrans = json_data.get("srcTrans")
        toTrans = json_data.get("toTrans")
      
        translate_text_prompt = translate(prompt, srcTrans, toTrans)
    
        return web.json_response({"translate_prompt": translate_text_prompt}) 
       
    return web.json_response({"translate_prompt": prompt})


def translate(prompt, srcTrans=None, toTrans=None):
    if not srcTrans:
        srcTrans = 'auto'
        
    if not toTrans:
        toTrans = 'en'

    translate_text_prompt = ''
    if prompt and prompt.strip() !="":
        translate_text_prompt = translator.translate(prompt, src=srcTrans, dest=toTrans)
    
    return translate_text_prompt.text if hasattr(translate_text_prompt, 'text') else ''

class TranslateCLIPTextEncodeNode:
    
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "from_translate": (['auto']+list(LANGUAGES.keys()), {"default": "auto"}),
                "to_translate": (list(LANGUAGES.keys()), {"default": "en"} ),
                "manual_translate": ([True, False],),      
                "text": ("STRING", {"multiline": True,"placeholder":"Input prompt"}),
                "clip": ("CLIP", )
                }
            }

    RETURN_TYPES = ("CONDITIONING","STRING",)
    FUNCTION = "translate_text"
    CATEGORY = "AlekPet Nodes/conditioning"

    def translate_text(self, **kwargs):        
        from_translate = kwargs.get("from_translate")
        to_translate = kwargs.get("to_translate")
        manual_translate = kwargs.get("manual_translate", False)
        text = kwargs.get("text")
        clip = kwargs.get("clip")
              
        text_tranlsated = translate(text, from_translate, to_translate) if not manual_translate else text
        tokens = clip.tokenize(text_tranlsated)
        cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)
        return ([[cond, {"pooled_output": pooled}]], text_tranlsated)
 

class TranslateTextNode(TranslateCLIPTextEncodeNode):

    @classmethod
    def INPUT_TYPES(self):
        return_types = super().INPUT_TYPES()
        del return_types["required"]["clip"]
        return return_types

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "translate_text"

    CATEGORY = "AlekPet Nodes/text"

    def translate_text(self, **kwargs):
        from_translate = kwargs.get("from_translate")
        to_translate = kwargs.get("to_translate")
        manual_translate = kwargs.get("manual_translate", False)
        text = kwargs.get("text")
        print(type(manual_translate))
              
        text_tranlsated = translate(text, from_translate, to_translate) if not manual_translate else text
        return (text_tranlsated,)
    
### =====  Translate Nodes [googletrans module] -> end ===== ###