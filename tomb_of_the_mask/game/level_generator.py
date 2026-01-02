import random
from collections import deque, defaultdict

WALL = "1"
FLOOR = "0"
COIN = "C"
EXIT = "E"
CRYSTAL = "K"
SPIKE = "S"
BAT = "B"

# ==========================================
# 1. ФІЗИКА ТА ВАЛІДАЦІЯ
# ==========================================

def get_slide_end(grid, r, c, dr, dc, treat_spike_as_wall=False):
    rows = len(grid)
    cols = len(grid[0])
    path = [(r, c)]
    curr_r, curr_c = r, c
    hit_spike = False
    
    while True:
        next_r, next_c = curr_r + dr, curr_c + dc
        if not (0 <= next_r < rows and 0 <= next_c < cols): break
        tile = grid[next_r][next_c]
        if tile == WALL: break
        if treat_spike_as_wall and tile == SPIKE:
            hit_spike = True
            break
        curr_r, curr_c = next_r, next_c
        path.append((curr_r, curr_c))
        
    return (curr_r, curr_c), path, hit_spike

def get_reachable_areas(grid, start_r, start_c, avoid_spikes=False):
    queue = deque([(start_r, start_c)])
    visited_stops = {(start_r, start_c)}
    reachable_path_cells = set()
    reachable_path_cells.add((start_r, start_c))
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    graph = defaultdict(list)
    
    while queue:
        r, c = queue.popleft()
        for dr, dc in directions:
            (stop_r, stop_c), path, hit_spike = get_slide_end(
                grid, r, c, dr, dc, treat_spike_as_wall=avoid_spikes
            )
            if avoid_spikes and hit_spike: continue
            
            if (stop_r, stop_c) != (r, c):
                graph[(r, c)].append((stop_r, stop_c))

            for cell in path: reachable_path_cells.add(cell)
            
            if (stop_r, stop_c) not in visited_stops:
                visited_stops.add((stop_r, stop_c))
                queue.append((stop_r, stop_c))
    return visited_stops, reachable_path_cells, graph

def is_strongly_connected(graph, all_nodes, start_node):
    if not all_nodes or start_node not in all_nodes: return False
    reverse_graph = defaultdict(list)
    for u, neighbors in graph.items():
        for v in neighbors: reverse_graph[v].append(u)
    
    can_reach_start = set()
    queue = deque([start_node])
    can_reach_start.add(start_node)
    
    while queue:
        curr = queue.popleft()
        for pred in reverse_graph[curr]:
            if pred not in can_reach_start:
                can_reach_start.add(pred)
                queue.append(pred)
                
    for node in all_nodes:
        if node not in can_reach_start: return False
    return True

# 👇 НОВА ФУНКЦІЯ: Рахує кількість свайпів від старту до кожної точки
def get_steps_from_start(graph, start_node):
    steps = {start_node: 0}
    queue = deque([start_node])
    
    while queue:
        curr = queue.popleft()
        curr_steps = steps[curr]
        
        for neighbor in graph[curr]:
            if neighbor not in steps:
                steps[neighbor] = curr_steps + 1
                queue.append(neighbor)
    return steps

# ==========================================
# 2. ДОПОМІЖНІ ФУНКЦІЇ ДЛЯ ВОРОГІВ
# ==========================================

def get_bat_flight_zone(grid, r, c):
    rows = len(grid)
    cols = len(grid[0])
    danger_cells = set()
    danger_cells.add((r, c))

    # Тільки горизонталь (оскільки ми зафіксували горизонтальний політ)
    curr = c - 1
    while curr > 0 and grid[r][curr] != WALL: 
        danger_cells.add((r, curr))
        curr -= 1
    
    curr = c + 1
    while curr < cols - 1 and grid[r][curr] != WALL: 
        danger_cells.add((r, curr))
        curr += 1
        
    return danger_cells

def check_space_for_bat(grid, r, c):
    rows = len(grid)
    cols = len(grid[0])
    
    neighbors = 0
    if grid[r+1][c] == FLOOR: neighbors += 1
    if grid[r-1][c] == FLOOR: neighbors += 1
    if grid[r][c+1] == FLOOR: neighbors += 1
    if grid[r][c-1] == FLOOR: neighbors += 1
    if neighbors < 2: return False 
    
    h_count = 1
    curr = c - 1
    while curr > 0 and grid[r][curr] != WALL: h_count += 1; curr -= 1
    curr = c + 1
    while curr < cols - 1 and grid[r][curr] != WALL: h_count += 1; curr += 1
        
    # Повертаємо True тільки якщо є горизонтальний простір >= 5
    if h_count >= 5: return True
    
    return False

# ==========================================
# 3. ГЕНЕРАЦІЯ
# ==========================================

def generate_directed_maze(rows, cols, difficulty):
    grid = [[WALL for _ in range(cols)] for _ in range(rows)]
    start_pos = (rows - 2, 1)
    target_zone_r = 1
    curr_r, curr_c = start_pos
    grid[curr_r][curr_c] = FLOOR
    spine_path = [start_pos]
    
    attempts = 0
    while curr_r > target_zone_r and attempts < 1000:
        attempts += 1
        moves = []
        if curr_r > 1: moves.extend([(-1, 0)] * 3)
        if curr_c < cols - 2: moves.extend([(0, 1)] * 2)
        if curr_c > 1: moves.extend([(0, -1)] * 2)
        if curr_r < rows - 2: moves.append((1, 0))
        
        if not moves: break
        dr, dc = random.choice(moves)
        
        segment_len = random.randint(1, 4)
        for _ in range(segment_len):
            nr, nc = curr_r + dr, curr_c + dc
            if 1 <= nr < rows - 1 and 1 <= nc < cols - 1:
                grid[nr][nc] = FLOOR
                curr_r, curr_c = nr, nc
                spine_path.append((nr, nc))
            else: break
    
    branch_density = min(0.5, 0.2 + (difficulty * 0.05))
    potential_branches = list(spine_path)
    random.shuffle(potential_branches)
    
    for i in range(int(len(spine_path) * branch_density)):
        br_r, br_c = potential_branches[i]
        branch_len = random.randint(2, 5 + difficulty)
        curr_br_r, curr_br_c = br_r, br_c
        for _ in range(branch_len):
            dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(dirs)
            moved = False
            for b_dr, b_dc in dirs:
                nr, nc = curr_br_r + b_dr*2, curr_br_c + b_dc*2
                if 1 <= nr < rows - 1 and 1 <= nc < cols - 1:
                    if grid[nr][nc] == WALL:
                        grid[curr_br_r + b_dr][curr_br_c + b_dc] = FLOOR
                        grid[nr][nc] = FLOOR
                        curr_br_r, curr_br_c = nr, nc
                        moved = True
                        break
            if not moved: break

    loop_chance = 0.05 + (difficulty * 0.03)
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if grid[r][c] == WALL:
                neighbors = 0
                for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    if grid[r+dr][c+dc] == FLOOR: neighbors += 1
                if neighbors >= 2 and random.random() < loop_chance:
                    grid[r][c] = FLOOR

    for r in range(rows): grid[r][0] = grid[r][cols - 1] = WALL
    for c in range(cols): grid[0][c] = grid[rows - 1][c] = WALL
    
    return grid, start_pos


def generate_level(rows, cols, coin_count=10, spawn_crystal=False):
    rows = max(rows, 11)
    cols = max(cols, 9)
    if rows % 2 == 0: rows += 1
    if cols % 2 == 0: cols += 1

    difficulty_tier = max(0, (rows - 15) // 2)
    target_coins = 10 + (difficulty_tier * 3)
    spike_count = 3 + difficulty_tier * 2
    
    if difficulty_tier >= 3:
        bat_count = min(6, 2 + (difficulty_tier - 3))
    else:
        bat_count = 0

    max_attempts = 2000

    for attempt in range(max_attempts):
        grid, start_pos = generate_directed_maze(rows, cols, difficulty_tier)
        start_r, start_c = start_pos

        reachable_stops, safe_cells, move_graph = get_reachable_areas(grid, start_r, start_c, avoid_spikes=True)
        if len(reachable_stops) < 5: continue
        if not is_strongly_connected(move_graph, reachable_stops, start_pos): continue

        # 👇 ВИЗНАЧЕННЯ ФІНІШУ НА ОСНОВІ КІЛЬКОСТІ КРОКІВ 👇
        # Отримуємо мапу кроків: скільки свайпів до кожної точки
        steps_map = get_steps_from_start(move_graph, start_pos)
        
        possible_exits = list(reachable_stops)
        if start_pos in possible_exits: possible_exits.remove(start_pos)
        
        # Фільтруємо ті, що фізично вгорі
        high_exits = [p for p in possible_exits if p[0] < rows // 2]
        
        candidates = high_exits if high_exits else possible_exits
        if not candidates: continue
        
        # Сортуємо кандидатів:
        # 1. За кількістю свайпів (чим більше, тим краще) -> це головний пріоритет
        # 2. За фізичною відстанню
        candidates.sort(key=lambda p: steps_map.get(p, 0), reverse=True)
        
        best_exit = candidates[0]
        exit_r, exit_c = best_exit
        
        # 👇 ПЕРЕВІРКА: Якщо до фінішу менше 5 ходів - це занадто просто, переробляємо
        min_required_steps = 5 + (difficulty_tier // 2) # Зі складністю росте вимога до довжини
        if steps_map.get(best_exit, 0) < min_required_steps:
            continue
            
        grid[exit_r][exit_c] = EXIT

        # ШИПИ
        potential_spikes = list(safe_cells)
        potential_spikes = [p for p in potential_spikes if p != start_pos and p != (exit_r, exit_c)]
        random.shuffle(potential_spikes)
        placed_spikes_count = 0
        for p in potential_spikes:
            if placed_spikes_count >= spike_count: break
            sr, sc = p
            grid[sr][sc] = SPIKE
            val_stops, _, val_graph = get_reachable_areas(grid, start_r, start_c, avoid_spikes=True)
            if (exit_r, exit_c) in val_stops and is_strongly_connected(val_graph, val_stops, start_pos):
                placed_spikes_count += 1
            else:
                grid[sr][sc] = FLOOR

        # КАЖАНИ
        _, final_safe_cells, _ = get_reachable_areas(grid, start_r, start_c, avoid_spikes=True)
        bat_danger_zones = set() 

        if bat_count > 0:
            potential_bats = []
            for r in range(1, rows - 1):
                # Ігноруємо рядки Старту та Фінішу
                if r == start_r or r == exit_r: continue

                for c in range(1, cols - 1):
                    if (grid[r][c] == FLOOR and (r,c) in final_safe_cells 
                        and (r,c) != start_pos and (r,c) != (exit_r, exit_c)):
                        
                        if check_space_for_bat(grid, r, c):
                            potential_bats.append((r, c))
            
            potential_bats = list(set(potential_bats))
            random.shuffle(potential_bats)
            placed_bats_pos = []
            
            for _ in range(bat_count):
                if not potential_bats: break
                br, bc = potential_bats.pop()
                
                too_close = False
                for (obr, obc) in placed_bats_pos:
                    if abs(br - obr) + abs(bc - obc) < 8:
                        too_close = True
                        break
                if too_close: continue

                grid[br][bc] = SPIKE 
                val_stops, _, val_graph = get_reachable_areas(grid, start_r, start_c, avoid_spikes=True)
                
                is_passable = (exit_r, exit_c) in val_stops and is_strongly_connected(val_graph, val_stops, start_pos)
                
                if is_passable:
                    grid[br][bc] = BAT
                    placed_bats_pos.append((br, bc))
                    flight_cells = get_bat_flight_zone(grid, br, bc)
                    bat_danger_zones.update(flight_cells)
                else:
                    grid[br][bc] = FLOOR

        # МОНЕТИ
        potential_coins = [
            p for p in final_safe_cells 
            if p != start_pos and p != (exit_r, exit_c) 
            and grid[p[0]][p[1]] != SPIKE 
            and grid[p[0]][p[1]] != BAT
            and p not in bat_danger_zones
        ]
        
        potential_coins.sort(key=lambda p: p[0], reverse=True)
        
        coins_to_place = min(len(potential_coins), target_coins)
        if coins_to_place < 5: continue 

        step = max(1, len(potential_coins) // coins_to_place)
        selected_coins = potential_coins[::step][:coins_to_place]
        
        if spawn_crystal:
            remaining = [p for p in potential_coins if p not in selected_coins]
            if remaining:
                random.shuffle(remaining)
                kx, ky = remaining.pop()
                grid[kx][ky] = CRYSTAL

        for r, c in selected_coins:
            grid[r][c] = COIN

        return ["".join(row) for row in grid], start_r, start_c

    print("FALLBACK LEVEL")
    grid = [[WALL for _ in range(cols)] for _ in range(rows)]
    for r in range(1, rows-1): grid[r][1] = FLOOR
    grid[rows-2][1] = FLOOR
    grid[1][1] = EXIT
    return ["".join(row) for row in grid], rows-2, 1