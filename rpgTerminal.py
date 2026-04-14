# this is a comment
import random
player_name = input("Enter your character's name: ")
player_health = 100
player_attack = 10
enemies_defeated = 0

print(f"Welcome, {player_name}! Your adventure begins...")
print(f"{player_name} has {player_health}  health, and {player_attack} attack. You have defeated {enemies_defeated} enemies")

def generate_enemy():
    enemy_types = ["Goblin", "Orc", "Skeleton"]
    enemy = random.choice(enemy_types)
    health = random.randint(20, 40)
    attack = random.randint(5, 12)
    return enemy, health, attack

#print(generate_enemy())

def battle(player_health, player_attack):
    enemy, enemy_health, enemy_attack = generate_enemy()
    print(f"A {enemy} appears! It has {enemy_health} health and {enemy_attack} attack.")
    while enemy_health > 0 and player_health > 0:
        print(f"Your Health: {player_health}")
        print(f"{enemy} Health: {enemy_health}")
        choice = input("Do you want to fight or run? ")
        if choice == "fight":
            damage = random.randint(5, player_attack)
            enemy_health = (enemy_health - damage)
            print(f"You hit the {enemy} for {damage} damage!")
            if enemy_health <= 0:
                print(f"You defeated the {enemy}!")
                return player_health, True
            damage = random.randint(3, enemy_attack)
            player_health -= damage
            print(f"The {enemy} hits your for {damage} damage!")
        elif choice == "run":
            chance = random.randint(1,2)
            if chance == 1:
                print("You escaped successfully!")
                return player_health, False
            else:
                print("You failed to escape!")
                damage = random.randint(3, enemy_attack)
                player_health -= damage
                print(f"The {enemy} hits your for {damage} damage!")
        else:
            print("Invalid choice. Please type 'fight' or 'run'.")


#battle(player_health, player_attack) 

while player_health > 0:
    print("You are exploring the world...")
    event = random.randint(1, 2)

    if event == 1:
        player_health, defeated = battle(player_health, player_attack)
        if defeated:
            enemies_defeated += 1
    else: 
        print("Nothing happens...")
    if enemies_defeated >= 3:
        print(f"Congratulations, {player_name}! You defeated 3 enemies and won!")
        break

if player_health <= 0:
    print(f"{player_name}, you have been defeated. Game Over!")

