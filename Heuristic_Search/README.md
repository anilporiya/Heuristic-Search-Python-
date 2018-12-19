Mendon Ponds Park

terrain.png is a sort of map of Mendon Ponds Park where each color(pixel value) represents a different type of terrain.

	Terrain_type		Color_on_map

	Open land			0
	Rough meadow			1
	Easy movement forest		2	
	Slow run forest			3
	Walk forest			4
	Impassible vegetation		5
	Lake/Swamp/Marsh		6
	Paved road			7
	Footpath			8		
	Out of bounds			9

mendonsearch.py implements an A* search between any two(within bounds) locations on the map with an admissible heuristic and prints the fastest path(and time it takes) between the given locations.

