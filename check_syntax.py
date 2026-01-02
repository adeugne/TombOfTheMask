import ast,traceback,sys
files = ['tomb_of_the_mask/game/level.py','tomb_of_the_mask/game/scenes/game_scene.py']
for f in files:
    try:
        ast.parse(open(f,'r',encoding='utf8').read())
        print(f, 'ok')
    except Exception:
        print('error in', f)
        traceback.print_exc()
        sys.exit(1)
