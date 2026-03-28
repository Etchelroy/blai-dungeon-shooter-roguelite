import pygame
import sys
import os

os.environ['SDL_AUDIODRIVER'] = 'dummy'

import settings
from settings import *
import assets
import menus
import effects
import audio

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("DUNGEON RIFT")
clock = pygame.time.Clock()

assets.preload_assets()
audio.init_audio()

class GameState:
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    PAUSED = "paused"
    DEAD = "dead"
    SHOP = "shop"
    CARD_SELECT = "card_select"
    CONTROLS = "controls"

def run_game_session():
    import camera, arena, tilemap, player, enemies, bosses, hud, shop as shop_mod
    import wave_manager, particles, lighting, spatial_hash, loot, projectiles, abilities, upgrades, ui

    cam = camera.Camera(SCREEN_W, SCREEN_H, ARENA_W, ARENA_H)
    effect_manager = effects.EffectManager(screen)
    particle_engine = particles.ParticleEngine()
    light_engine = lighting.LightingEngine(ARENA_W, ARENA_H, TILE_SIZE_SCALED)
    sp_hash = spatial_hash.SpatialHash(cell_size=96)

    arena_map = arena.generate_arena()
    tile_map = tilemap.TileMap(arena_map, particle_engine)

    p = player.Player(ARENA_W // 2, ARENA_H // 2, particle_engine, effect_manager)
    upgrade_mgr = upgrades.UpgradeManager(p)
    wave_mgr = wave_manager.WaveManager(p, tile_map, particle_engine, effect_manager)
    loot_mgr = loot.LootManager(particle_engine)
    hud_renderer = hud.HUD(screen, p, wave_mgr, tile_map)
    shop_screen = shop_mod.Shop(screen, p, upgrade_mgr)
    proj_pool = projectiles.ProjectilePool(particle_engine, effect_manager)

    p.proj_pool = proj_pool
    p.loot_mgr = loot_mgr
    wave_mgr.proj_pool = proj_pool
    wave_mgr.loot_mgr = loot_mgr
    wave_mgr.sp_hash = sp_hash

    font_big = pygame.font.SysFont(None, 72)
    font_med = pygame.font.SysFont(None, 36)

    game_surface = pygame.Surface((SCREEN_W, SCREEN_H))
    running = True
    state = GameState.PLAYING
    pause_menu = menus.PauseMenu(screen)
    card_select = None
    dt_scale = 1.0
    wave_trans_timer = 0.0
    wave_trans_msg = ""
    combo_flash_timer = 0.0

    while running:
        raw_dt = clock.tick(FPS) / 1000.0
        raw_dt = min(raw_dt, 0.05)
        dt = raw_dt * effect_manager.slow_mo_scale * dt_scale

        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                return "quit"
            if ev.type == pygame.KEYDOWN:
                if state == GameState.PLAYING:
                    if ev.key == pygame.K_ESCAPE:
                        state = GameState.PAUSED
                    p.handle_keydown(ev)
                elif state == GameState.PAUSED:
                    result = pause_menu.handle_event(ev)
                    if result == "resume":
                        state = GameState.PLAYING
                    elif result == "quit":
                        return "main_menu"
                elif state == GameState.CARD_SELECT:
                    result = card_select.handle_event(ev)
                    if result:
                        upgrade_mgr.apply_upgrade(result)
                        state = GameState.PLAYING
                        wave_mgr.start_next_wave()
                elif state == GameState.SHOP:
                    result = shop_screen.handle_event(ev)
                    if result == "done":
                        card_select = menus.CardSelectMenu(screen, upgrade_mgr.get_random_upgrades(3))
                        state = GameState.CARD_SELECT
            if ev.type == pygame.KEYUP:
                if state == GameState.PLAYING:
                    p.handle_keyup(ev)
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if state == GameState.PLAYING:
                    p.handle_mouse_down(ev)
                elif state == GameState.CARD_SELECT:
                    result = card_select.handle_mouse(ev)
                    if result:
                        upgrade_mgr.apply_upgrade(result)
                        state = GameState.PLAYING
                        wave_mgr.start_next_wave()
                elif state == GameState.SHOP:
                    result = shop_screen.handle_mouse(ev)
                    if result == "done":
                        card_select = menus.CardSelectMenu(screen, upgrade_mgr.get_random_upgrades(3))
                        state = GameState.CARD_SELECT
            if ev.type == pygame.MOUSEBUTTONUP:
                if state == GameState.PLAYING:
                    p.handle_mouse_up(ev)

        if state == GameState.PLAYING:
            mx, my = pygame.mouse.get_pos()
            world_mx = mx + cam.offset_x
            world_my = my + cam.offset_y
            p.update(dt, tile_map, world_mx, world_my)
            wave_mgr.update(dt, p, cam)
            proj_pool.update(dt, tile_map, wave_mgr.enemies, wave_mgr.boss, p, sp_hash, loot_mgr)
            particle_engine.update(dt)
            loot_mgr.update(dt, p)
            effect_manager.update(raw_dt)
            sp_hash.clear()
            sp_hash.insert_many(wave_mgr.enemies)
            if wave_mgr.boss:
                sp_hash.insert(wave_mgr.boss)
            cam.update(p.x, p.y, dt)

            if p.dead:
                effect_manager.start_flash((255,50,50), 0.5)
                return "dead", wave_mgr.wave_num, p.score, p.kills, p.coins

            if wave_mgr.wave_cleared and not wave_mgr.boss_wave:
                wave_mgr.wave_cleared = False
                if wave_mgr.wave_num % 3 == 0:
                    shop_screen.restock()
                    state = GameState.SHOP
                else:
                    card_select = menus.CardSelectMenu(screen, upgrade_mgr.get_random_upgrades(3))
                    state = GameState.CARD_SELECT

            if wave_mgr.wave_trans_timer > 0:
                wave_trans_timer = wave_mgr.wave_trans_timer
                wave_trans_msg = wave_mgr.wave_trans_msg

        game_surface.fill(BG_COLOR)

        tile_map.draw(game_surface, cam)
        loot_mgr.draw(game_surface, cam)
        for enemy in wave_mgr.enemies:
            enemy.draw(game_surface, cam)
        if wave_mgr.boss:
            wave_mgr.boss.draw(game_surface, cam)
        proj_pool.draw(game_surface, cam)
        p.draw(game_surface, cam)
        particle_engine.draw(game_surface, cam)
        light_engine.draw(game_surface, cam, tile_map, p, wave_mgr.enemies)

        screen.blit(game_surface, (0, 0))

        hud_renderer.draw(wave_mgr)
        effect_manager.draw_overlay()

        if wave_trans_timer > 0:
            wave_trans_timer -= raw_dt
            alpha = min(255, int(wave_trans_timer * 400))
            surf = font_big.render(wave_trans_msg, True, (255, 220, 50))
            surf.set_alpha(alpha)
            screen.blit(surf, (SCREEN_W//2 - surf.get_width()//2, SCREEN_H//2 - 60))

        if state == GameState.PAUSED:
            pause_menu.draw()
        elif state == GameState.CARD_SELECT:
            card_select.draw()
        elif state == GameState.SHOP:
            shop_screen.draw()

        pygame.display.flip()

    return "quit"

def main():
    main_menu = menus.MainMenu(screen)
    controls_menu = menus.ControlsMenu(screen)
    death_screen = menus.DeathScreen(screen)
    state = GameState.MAIN_MENU
    death_stats = None

    while True:
        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if state == GameState.MAIN_MENU:
                result = main_menu.handle_event(ev)
                if result == "start":
                    state = GameState.PLAYING
                elif result == "controls":
                    state = GameState.CONTROLS
                elif result == "quit":
                    pygame.quit()
                    sys.exit()
            elif state == GameState.CONTROLS:
                result = controls_menu.handle_event(ev)
                if result == "back":
                    state = GameState.MAIN_MENU
            elif state == GameState.DEAD:
                result = death_screen.handle_event(ev)
                if result == "restart":
                    state = GameState.PLAYING
                elif result == "menu":
                    state = GameState.MAIN_MENU

        if state == GameState.MAIN_MENU:
            clock.tick(FPS)
            main_menu.update(clock.get_time() / 1000.0)
            main_menu.draw()
            pygame.display.flip()
        elif state == GameState.CONTROLS:
            clock.tick(FPS)
            controls_menu.draw()
            pygame.display.flip()
        elif state == GameState.DEAD:
            clock.tick(FPS)
            death_screen.update(clock.get_time() / 1000.0)
            death_screen.draw(death_stats)
            pygame.display.flip()
        elif state == GameState.PLAYING:
            result = run_game_session()
            if result == "quit":
                pygame.quit()
                sys.exit()
            elif result == "main_menu":
                state = GameState.MAIN_MENU
            elif isinstance(result, tuple) and result[0] == "dead":
                death_stats = result[1:]
                death_screen.reset()
                state = GameState.DEAD

if __name__ == "__main__":
    main()