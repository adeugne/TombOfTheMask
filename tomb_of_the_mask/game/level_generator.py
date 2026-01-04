import random
from collections import deque, defaultdict

WALL = "1"
FLOOR = "0"
COIN = "C"
EXIT = "E"
CRYSTAL = "K"
SPIKE = "S"
BAT = "B"
LIFE = "L"

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
        if treat_spike_as_wall and (tile == SPIKE or tile == BAT):
            hit_spike = True
            break
        curr_r, curr_c = next_r, next_c
        path.append((curr_r, curr_c))
        
    return (curr_r, curr_c), path, hit_spike

def get_reachable_areas(grid, start_r, start_c, avoid_danger=False):
    queue = deque([(start_r, start_c)])
    visited_stops = {(start_r, start_c)}
    reachable_path_cells = set()
    reachable_path_cells.add((start_r, start_c))
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    graph = defaultdict(list)
    
    while queue:
        r, c = queue.popleft()
        for dr, dc in directions:
            (stop_r, stop_c), path, hit_danger = get_slide_end(
                grid, r, c, dr, dc, treat_spike_as_wall=avoid_danger
            )
            
            if avoid_danger and hit_danger: continue
            
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

    curr = c - 1
    while curr > 0 and grid[r][curr] != WALL: 
        danger_cells.add((r, curr)); curr -= 1
    
    curr = c + 1
    while curr < cols - 1 and grid[r][curr] != WALL: 
        danger_cells.add((r, curr)); curr += 1
        
    return danger_cells

def check_space_for_bat(grid, r, c):
    rows = len(grid)
    cols = len(grid[0])
    
    if grid[r+1][c] != FLOOR: return False
    if grid[r-1][c] != FLOOR: return False
    if grid[r][c+1] != FLOOR: return False
    if grid[r][c-1] != FLOOR: return False
    
    h_count = 1
    curr = c - 1
    while curr > 0 and grid[r][curr] != WALL: h_count += 1; curr -= 1
    curr = c + 1
    while curr < cols - 1 and grid[r][curr] != WALL: h_count += 1; curr += 1
    if h_count >= 5: return True
    return False

# ==========================================
# 3. ГЕНЕРАТОР "СПРЯМОВАНИЙ ЛАБІРИНТ"
# ==========================================

def generate_directed_maze(rows, cols, difficulty):
    grid = [[WALL for _ in range(cols)] for _ in range(rows)]
    start_pos = (rows - 2, 1)
    grid[start_pos[0]][start_pos[1]] = FLOOR

    def in_bounds(r, c):
        return 1 <= r < rows - 1 and 1 <= c < cols - 1

    stack = [start_pos]
    visited = {start_pos}
    dirs = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    while stack:
        r, c = stack[-1]
        candidates = []
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc):
                continue
            if (nr, nc) in visited:
                continue
            weight = 3 if dr == -2 else (2 if dr == 0 else 1)
            candidates.extend([(dr, dc)] * weight)

        if not candidates:
            stack.pop()
            continue

        dr, dc = random.choice(candidates)
        wall_r, wall_c = r + dr // 2, c + dc // 2
        nr, nc = r + dr, c + dc
        grid[wall_r][wall_c] = FLOOR
        grid[nr][nc] = FLOOR
        visited.add((nr, nc))
        stack.append((nr, nc))

    room_attempts = max(2, 2 + difficulty)
    for _ in range(room_attempts):
        size = 3 if random.random() < 0.85 else 5
        half = size // 2
        rr = random.randint(2 + half, rows - 3 - half)
        cc = random.randint(2 + half, cols - 3 - half)
        for r in range(rr - half, rr + half + 1):
            for c in range(cc - half, cc + half + 1):
                if in_bounds(r, c):
                    grid[r][c] = FLOOR

    corridor_attempts = 4 + (difficulty * 2)
    floor_cells = [
        (r, c)
        for r in range(1, rows - 1)
        for c in range(1, cols - 1)
        if grid[r][c] == FLOOR
    ]
    for _ in range(corridor_attempts):
        if not floor_cells:
            break
        r, c = random.choice(floor_cells)
        dr, dc = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        length = random.randint(5, 10 + (difficulty * 2))
        for _ in range(length):
            if random.random() < 0.7:
                dr, dc = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc):
                break
            grid[nr][nc] = FLOOR
            r, c = nr, nc

    loop_chance = 0.06 + (difficulty * 0.05)
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if grid[r][c] == WALL:
                neighbors = 0
                for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    if grid[r+dr][c+dc] == FLOOR: neighbors += 1
                if neighbors >= 2 and random.random() < loop_chance:
                    grid[r][c] = FLOOR

    def floor_neighbors(r, c):
        count = 0
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            if grid[r + dr][c + dc] == FLOOR:
                count += 1
        return count

    braid_chance = min(0.8, 0.35 + (difficulty * 0.07))
    dead_ends = [
        (r, c)
        for r in range(1, rows - 1)
        for c in range(1, cols - 1)
        if grid[r][c] == FLOOR and floor_neighbors(r, c) == 1
    ]
    random.shuffle(dead_ends)
    for r, c in dead_ends:
        if random.random() > braid_chance:
            continue
        candidates = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            wall_r, wall_c = r + dr, c + dc
            next_r, next_c = r + dr * 2, c + dc * 2
            if not in_bounds(next_r, next_c):
                continue
            if grid[wall_r][wall_c] == WALL and grid[next_r][next_c] == FLOOR:
                candidates.append((wall_r, wall_c))
        if candidates:
            wall_r, wall_c = random.choice(candidates)
            grid[wall_r][wall_c] = FLOOR

    extra_openings = min(40, 6 + (difficulty * 5))
    for _ in range(extra_openings):
        r = random.randint(2, rows - 3)
        c = random.randint(2, cols - 3)
        if grid[r][c] == WALL:
            neighbors = 0
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                if grid[r + dr][c + dc] == FLOOR:
                    neighbors += 1
            if neighbors >= 2:
                grid[r][c] = FLOOR

    for r in range(rows): grid[r][0] = grid[r][cols - 1] = WALL
    for c in range(cols): grid[0][c] = grid[rows - 1][c] = WALL
    
    return grid, start_pos


def generate_level(rows, cols, coin_count=10, spawn_crystal=False, spawn_life=False, current_level=1):
    rows = max(rows, 11)
    cols = max(cols, 9)
    if rows % 2 == 0: rows += 1
    if cols % 2 == 0: cols += 1

    difficulty_tier = max(0, (rows - 15) // 2)
    target_coins = 10 + (difficulty_tier * 3)
    spike_count = 3 + difficulty_tier * 2
    


    # Bat spawn logic - very high base chance from level 12, aggressive growth from level 15, almost guaranteed from level 16
    if current_level >= 1:
        # From level 12-14: 85% base chance
        # From level 15: 100% guaranteed spawn, with increasing count
        # From level 16+: Almost always spawn (very high count guarantee)
        if current_level < 15:
            bat_spawn_chance = 1
            base_bat_count = 2 
            # + ((current_level - 12) // 2)
        elif current_level == 15:
            bat_spawn_chance = 1.0
            base_bat_count = 2
        else:
            bat_spawn_chance = 1.0
            growth_levels = current_level - 16
            base_bat_count = 6 + (growth_levels * 2) 
        
        if random.random() < bat_spawn_chance:
            bat_count = min(20, base_bat_count + random.randint(2, 4))  
        else:
            bat_count = max(3, base_bat_count - 1)
    else:
        bat_count = 0


    max_attempts = 2000

    for attempt in range(max_attempts):
        grid, start_pos = generate_directed_maze(rows, cols, difficulty_tier)
        start_r, start_c = start_pos

        reachable_stops, safe_cells, move_graph = get_reachable_areas(grid, start_r, start_c, avoid_danger=True)
        if len(reachable_stops) < 5: continue
        if not is_strongly_connected(move_graph, reachable_stops, start_pos): continue

        steps_map = get_steps_from_start(move_graph, start_pos)
        possible_exits = list(reachable_stops)
        if start_pos in possible_exits: possible_exits.remove(start_pos)
        high_exits = [p for p in possible_exits if p[0] < rows // 2]
        candidates = high_exits if high_exits else possible_exits
        if not candidates: continue
        
        candidates.sort(key=lambda p: steps_map.get(p, 0), reverse=True)
        best_exit = candidates[0]
        exit_r, exit_c = best_exit
        
        min_required_steps = 5 + (difficulty_tier // 2)
        if steps_map.get(best_exit, 0) < min_required_steps: continue
            
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
            val_stops, _, val_graph = get_reachable_areas(grid, start_r, start_c, avoid_danger=True)
            if (exit_r, exit_c) in val_stops and is_strongly_connected(val_graph, val_stops, start_pos):
                placed_spikes_count += 1
            else:
                grid[sr][sc] = FLOOR

        # КАЖАНИ
        _, current_safe_cells, _ = get_reachable_areas(grid, start_r, start_c, avoid_danger=True)
        bat_danger_zones = set() 

        if bat_count > 0:
            potential_bats = []
            for r in range(1, rows - 1):
                if r == start_r or r == exit_r: continue
                for c in range(1, cols - 1):
                    if (grid[r][c] == FLOOR and (r,c) in current_safe_cells 
                        and (r,c) != start_pos and (r,c) != (exit_r, exit_c)):
                        if check_space_for_bat(grid, r, c):
                            potential_bats.append((r, c))
            
            potential_bats = list(set(potential_bats))
            random.shuffle(potential_bats)
            placed_bats_pos = []
            
            for _ in range(bat_count):
                if not potential_bats: break
                br, bc = potential_bats.pop()
                level_bonus = min(0.2, max(0, current_level - 15) * 0.02)
                bat_individual_chance = min(0.98, 0.7 + (difficulty_tier * 0.08) + level_bonus)
                if random.random() > bat_individual_chance:
                    continue 
                
                too_close = False
                for (obr, obc) in placed_bats_pos:
                    if abs(br - obr) + abs(bc - obc) < 6:
                        too_close = True; break
                if too_close: continue

                flight_zone = get_bat_flight_zone(grid, br, bc)
                
                original_tiles = {}
                for f_r, f_c in flight_zone:
                    original_tiles[(f_r, f_c)] = grid[f_r][f_c]
                    grid[f_r][f_c] = SPIKE 
                
                val_stops, val_cells, val_graph = get_reachable_areas(grid, start_r, start_c, avoid_danger=True)
                
                is_valid = (
                    (exit_r, exit_c) in val_stops and 
                    is_strongly_connected(val_graph, val_stops, start_pos)
                )
                
                for (f_r, f_c), tile in original_tiles.items():
                    grid[f_r][f_c] = tile
                
                if is_valid:
                    grid[br][bc] = BAT
                    placed_bats_pos.append((br, bc))
                    bat_danger_zones.update(flight_zone)
                    _, current_safe_cells, _ = get_reachable_areas(grid, start_r, start_c, avoid_danger=True)

        # МОНЕТИ ТА БОНУСИ
        _, accessible_cells, _ = get_reachable_areas(grid, start_r, start_c, avoid_danger=True)
        
        final_valid_spots = [
            p for p in accessible_cells 
            if p != start_pos and p != (exit_r, exit_c)
            and grid[p[0]][p[1]] == FLOOR
            and p not in bat_danger_zones
        ]
        
        final_valid_spots.sort(key=lambda p: p[0], reverse=True)
        
        coins_to_place = min(len(final_valid_spots), target_coins)
        if coins_to_place < 5: continue 

        step = max(1, len(final_valid_spots) // coins_to_place)
        selected_coins = final_valid_spots[::step][:coins_to_place]
        
        # Залишок місць для бонусів
        bonus_spots = [p for p in final_valid_spots if p not in selected_coins]
        random.shuffle(bonus_spots)

        # 1. Кристал
        if spawn_crystal and bonus_spots:
            kx, ky = bonus_spots.pop()
            grid[kx][ky] = CRYSTAL
            
        # 2. Життя 
        if spawn_life and bonus_spots:
            lx, ly = bonus_spots.pop()
            grid[lx][ly] = LIFE

        for r, c in selected_coins:
            grid[r][c] = COIN

        return ["".join(row) for row in grid], start_r, start_c

    print("FALLBACK LEVEL")
    grid = [[WALL for _ in range(cols)] for _ in range(rows)]
    for r in range(1, rows-1): grid[r][1] = FLOOR
    grid[rows-2][1] = FLOOR
    grid[1][1] = EXIT
    return ["".join(row) for row in grid], rows-2, 1
