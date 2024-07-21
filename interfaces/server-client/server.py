import os

import base64
from aiohttp import web
from aiohttp_cors import setup, ResourceOptions
from controller import controller

controller = controller()

async def handle_generate(request):
    data = await request.json()
    input = data['input']
    response = controller.generate_response(input)
    return web.json_response(response)

async def handle_listen(request):
    if request.content_type == 'multipart/form-data':
        reader = await request.multipart()
        field = await reader.next()
        with open('user_speech.wav', 'wb') as f:
            while True:
                chunk = await field.read_chunk()
                if not chunk:
                    break
                f.write(chunk)
        response = controller.listen(os.path.abspath(f.name))
        return web.json_response(response)
    else:
        data = await request.json()
        input = data['input']
        response = controller.listen(input)
        return web.json_response(response)

async def handle_speak(request):
    data = await request.json()
    input = data['input']
    userinput, output, audio_output = controller.speak(input)
    response = {'userinput': userinput, 'output': output}
    return web.json_response(response, headers={'X-Audio-Output': audio_output})


async def handle_full(request):
    if request.content_type == 'multipart/form-data':
        reader = await request.multipart()
        field = await reader.next()
        with open('speech.wav', 'wb') as f:
            while True:
                chunk = await field.read_chunk()
                if not chunk:
                    break
                f.write(chunk)
        userinput, output, audio_output = controller.full_pipeline(os.path.abspath(f.name))

        if audio_output is not None:
            with open(audio_output, 'rb') as audio_file:
                audio_bytes = audio_file.read()
        else:
            audio_bytes = ""

        headers = {'Audio-Output': audio_bytes}
        response = {'userinput': userinput, 'output': output}
        
        return web.json_response(response, headers=headers)
    else:
        data = await request.json()
        input = data['input']
        userinput, output, audio_output = controller.full_pipeline(input)

        if audio_output is None:
            with open(audio_output, 'rb') as audio_file:
                audio_bytes = audio_file.read()
        else:
            audio_bytes = ""
        
        headers = {'Audio-Output': audio_bytes}
        response = {'userinput': userinput, 'output': output}
       
        return web.json_response(response, headers=headers)



async def handle_text(request):
    data = await request.json()
    input = data['input']
    userinput, output, audio_output = controller.text_pipeline(input)
    response = {'userinput': userinput, 'output': output}
    return web.json_response(response, headers={'X-Audio-Output': audio_output})

async def handle_command(request):
    data = await request.json()
    input = data['input']
    if input == 'None':
        response = {'response': 'No command provided.'}
    else:
        response = controller.evaluate(input)
    return web.json_response(response)

app = web.Application()

cors = setup(app, defaults={
    "*": ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

app.add_routes([web.post('/api/v1/full', handle_full)])
app.add_routes([web.post('/api/v1/text', handle_text)])
app.add_routes([web.post('/api/v1/generate', handle_generate)])
app.add_routes([web.post('/api/v1/listen', handle_listen)])
app.add_routes([web.post('/api/v1/speak', handle_speak)])
app.add_routes([web.post('/api/v1/command', handle_command)])

for route in list(app.router.routes()):
    cors.add(route)

if __name__ == '__main__':
    web.run_app(app, port=6166, host='0.0.0.0')