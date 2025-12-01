# Movimientos
IDLE = 0
LEFT_DOWN = 1
RIGHT_DOWN = 2
UP = 3
DOWN = 4

# Posturas
DEATH_SPRITE = 7
IDLE_SPRITE = 3
WALK_SPRITE = 0
ATTACK_SPRITE = 12  # Nueva constante para la animación de ataque
HURT_SPRITE = 16 
SHOOT_SPRITE = 20  # Nueva constante para la animación de disparo

# Estados del enemigo
STATE_IDLE = 0
STATE_PATROL = 1
STATE_CHASE = 2
STATE_ATTACK = 3
STATE_HURT = 4  # Nueva constante para el estado de daño
STATE_SHOOT = 5  # Nueva constante para el estado de disparo

# Modificar las constantes de posturas para que coincidan con el orden en el archivo coordPlayer.txt
DOWN_ROW = 0    # Primera fila: sprites caminando hacia abajo
LEFT_ROW = 1    # Segunda fila: sprites caminando hacia la izquierda
RIGHT_ROW = 2   # Tercera fila: sprites caminando hacia la derecha
UP_ROW = 3      # Cuarta fila: sprites caminando hacia arriba

# Añadir nuevas constantes para animación de melee
MELEE_DOWN_ROW = 12    # Fila para ataque melee hacia abajo
MELEE_LEFT_ROW = 13    # Fila para ataque melee hacia la izquierda
MELEE_RIGHT_ROW = 14   # Fila para ataque melee hacia la derecha
MELEE_UP_ROW = 15      # Fila para ataque melee hacia arriba

# Añadir nuevas constantes para animación de disparo
SHOOT_DOWN_ROW = 20    # Fila para disparo hacia abajo
SHOOT_LEFT_ROW = 21    # Fila para disparo hacia la izquierda
SHOOT_RIGHT_ROW = 22   # Fila para disparo hacia la derecha
SHOOT_UP_ROW = 23      # Fila para disparo hacia arriba

# Velocidades de los distintos personajes
ANIMATION_SPEED = 5 # updates que durará cada imagen del personaje
                              # debería de ser un valor distinto para cada postura