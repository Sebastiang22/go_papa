import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.mysql_inventory_manager import MySQLInventoryManager

async def add_go_papa_menu_items():
    """Add Go Papa menu items to the inventory."""
    inventory_manager = MySQLInventoryManager()
    restaurant_id = "go_papa"
    
    # Menu items with their details and descriptions
    menu_items = [
        # Go Papa
        {
            "name": "Go Papa X2", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 50000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Carne mechada, Chicharrón, Chorizo, Hogao, Huevos de codorniz, Salsa Go Papa, Queso Fundido",
            "tipo_producto": "menu"
        },
        {
            "name": "Go Papa Familiar", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 85000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Carne mechada, Chicharrón, Chorizo, Hogao, Huevos de codorniz, Salsa Go Papa, Queso Fundido. Tamaño familiar.",
            "tipo_producto": "menu"
        },
        
        # La Gringa
        {
            "name": "La Gringa X2", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 50000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Pulled Pork, Chicharrón, Maicitos, Pico e gallo, Cebolla crispy, Sour Cream, Queso Fundido",
            "tipo_producto": "menu"
        },
        {
            "name": "La Gringa Familiar", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 85000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Pulled Pork, Chicharrón, Maicitos, Pico e gallo, Cebolla crispy, Sour Cream, Queso Fundido. Tamaño familiar.",
            "tipo_producto": "menu"
        },
        
        # Chicken
        {
            "name": "Chicken X2", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 45000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Pollo, Tocineta, Maicitos, Salsa Go Papa, Queso Fundido",
            "tipo_producto": "menu"
        },
        {
            "name": "Chicken Familiar", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 75000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Pollo, Tocineta, Maicitos, Salsa Go Papa, Queso Fundido. Tamaño familiar.",
            "tipo_producto": "menu"
        },
        
        # La Mexa
        {
            "name": "La Mexa X2", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 45000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Carne mechada, Pico e gallo, Salsa Roja Picosa, Guacamole, Salsa Go Papa, Queso Fundido",
            "tipo_producto": "menu"
        },
        {
            "name": "La Mexa Familiar", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 75000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Carne mechada, Pico e gallo, Salsa Roja Picosa, Guacamole, Salsa Go Papa, Queso Fundido. Tamaño familiar.",
            "tipo_producto": "menu"
        },
        
        # Hawaiana
        {
            "name": "Hawaiana X2", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 45000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Pollo, Tocineta, Piña, Salsa Go Papa, Queso Fundido",
            "tipo_producto": "menu"
        },
        {
            "name": "Hawaiana Familiar", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 75000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Pollo, Tocineta, Piña, Salsa Go Papa, Queso Fundido. Tamaño familiar.",
            "tipo_producto": "menu"
        },
        
        # Montañera
        {
            "name": "Montañera X2", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 45000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Costilla, Maduro Calado, Salsa Go Papa, Queso Fundido",
            "tipo_producto": "menu"
        },
        {
            "name": "Montañera Familiar", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 75000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Costilla, Maduro Calado, Salsa Go Papa, Queso Fundido. Tamaño familiar.",
            "tipo_producto": "menu"
        },
        
        # La 21
        {
            "name": "La 21 X2", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 45000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Chorizo, Carne Mechada, Guacamole, Salsa Go Papa, Queso Fundido",
            "tipo_producto": "menu"
        },
        {
            "name": "La 21 Familiar", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 75000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Chorizo, Carne Mechada, Guacamole, Salsa Go Papa, Queso Fundido. Tamaño familiar.",
            "tipo_producto": "menu"
        },
        
        # Flamenca
        {
            "name": "Flamenca X2", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 35000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Chorizo Español, Jamón Serrano, Salsa Brava, Paprika, Salsa Go Papa, Queso Fundido",
            "tipo_producto": "menu"
        },
        {
            "name": "Flamenca Familiar", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 75000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Chorizo Español, Jamón Serrano, Salsa Brava, Paprika, Salsa Go Papa, Queso Fundido. Tamaño familiar.",
            "tipo_producto": "menu"
        },
        
        # Italiana
        {
            "name": "Italiana X2", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 35000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Salami, Aderezo napolitano, Queso Fundido",
            "tipo_producto": "menu"
        },
        {
            "name": "Italiana Familiar", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 75000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Salami, Aderezo napolitano, Queso Fundido. Tamaño familiar.",
            "tipo_producto": "menu"
        },
        
        # Clásica
        {
            "name": "Clasica X2", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 25000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Salsa Go Papa, Queso Fundido",
            "tipo_producto": "menu"
        },
        {
            "name": "Clasica Familiar", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 75000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Salsa Go Papa, Queso Fundido. Tamaño familiar.",
            "tipo_producto": "menu"
        },
        
        # Go Papita
        {
            "name": "Go Papita", 
            "quantity": 10, 
            "unit": "porción", 
            "price": 21000, 
            "descripcion": "Papas fritas, Salchicha Llanera, Nuggets de pollo, Jugo Hit 200ml",
            "tipo_producto": "menu"
        },

        # Bebidas
        {
            "name": "Agua", 
            "quantity": 20, 
            "unit": "unidad", 
            "price": 3000, 
            "descripcion": "Botella de agua mineral",
            "tipo_producto": "menu"
        },
        {
            "name": "Soda", 
            "quantity": 20, 
            "unit": "unidad", 
            "price": 5000, 
            "descripcion": "Soda/Gaseosa personal",
            "tipo_producto": "menu"
        },
        {
            "name": "Hit 200 ml", 
            "quantity": 20, 
            "unit": "unidad", 
            "price": 3000, 
            "descripcion": "Jugo Hit personal 200ml",
            "tipo_producto": "menu"
        },
        {
            "name": "Hit 400 ml", 
            "quantity": 20, 
            "unit": "unidad", 
            "price": 5000, 
            "descripcion": "Jugo Hit personal 400ml",
            "tipo_producto": "menu"
        },
        {
            "name": "Hit Familiar", 
            "quantity": 20, 
            "unit": "unidad", 
            "price": 8000, 
            "descripcion": "Jugo Hit tamaño familiar",
            "tipo_producto": "menu"
        },
        {
            "name": "Cerveza Poker", 
            "quantity": 20, 
            "unit": "unidad", 
            "price": 6000, 
            "descripcion": "Cerveza Poker fría",
            "tipo_producto": "menu"
        },
        {
            "name": "Coca Cola", 
            "quantity": 20, 
            "unit": "unidad", 
            "price": 5000, 
            "descripcion": "Coca Cola personal",
            "tipo_producto": "menu"
        },
        {
            "name": "Coca Cola Zero", 
            "quantity": 20, 
            "unit": "unidad", 
            "price": 5000, 
            "descripcion": "Coca Cola Zero personal",
            "tipo_producto": "menu"
        },
        {
            "name": "Coca Cola 1.5 Lt", 
            "quantity": 20, 
            "unit": "unidad", 
            "price": 9000, 
            "descripcion": "Coca Cola 1.5 litros",
            "tipo_producto": "menu"
        },
        {
            "name": "Postobón 1.5 Lt", 
            "quantity": 20, 
            "unit": "unidad", 
            "price": 8000, 
            "descripcion": "Postobón 1.5 litros",
            "tipo_producto": "menu"
        },
        {
            "name": "Coca Cola 3 Lt", 
            "quantity": 20, 
            "unit": "unidad", 
            "price": 16000, 
            "descripcion": "Coca Cola 3 litros",
            "tipo_producto": "menu"
        },
        
        # Adiciones
        {
            "name": "Porción extra de papas", 
            "quantity": 30, 
            "unit": "porción", 
            "price": 8000, 
            "descripcion": "Porción adicional de papas fritas",
            "tipo_producto": "adicion"
        },
        {
            "name": "Queso extra", 
            "quantity": 30, 
            "unit": "porción", 
            "price": 5000, 
            "descripcion": "Porción adicional de queso fundido",
            "tipo_producto": "adicion"
        },
        {
            "name": "Salchicha extra", 
            "quantity": 30, 
            "unit": "unidad", 
            "price": 7000, 
            "descripcion": "Salchicha Llanera adicional",
            "tipo_producto": "adicion"
        },
        {
            "name": "Chorizo extra", 
            "quantity": 30, 
            "unit": "unidad", 
            "price": 6000, 
            "descripcion": "Porción adicional de chorizo",
            "tipo_producto": "adicion"
        },
        {
            "name": "Pollo extra", 
            "quantity": 30, 
            "unit": "porción", 
            "price": 8000, 
            "descripcion": "Porción adicional de pollo",
            "tipo_producto": "adicion"
        },
        {
            "name": "Carne mechada extra", 
            "quantity": 30, 
            "unit": "porción", 
            "price": 8000, 
            "descripcion": "Porción adicional de carne mechada",
            "tipo_producto": "adicion"
        },
        {
            "name": "Guacamole extra", 
            "quantity": 30, 
            "unit": "porción", 
            "price": 4000, 
            "descripcion": "Porción adicional de guacamole",
            "tipo_producto": "adicion"
        },
        {
            "name": "Maicitos extra", 
            "quantity": 30, 
            "unit": "porción", 
            "price": 3000, 
            "descripcion": "Porción adicional de maíz tierno",
            "tipo_producto": "adicion"
        },
        {
            "name": "Tocineta extra", 
            "quantity": 30, 
            "unit": "porción", 
            "price": 5000, 
            "descripcion": "Porción adicional de tocineta",
            "tipo_producto": "adicion"
        },
        {
            "name": "Chicharrón extra", 
            "quantity": 30, 
            "unit": "porción", 
            "price": 5000, 
            "descripcion": "Porción adicional de chicharrón",
            "tipo_producto": "adicion"
        },
        {
            "name": "Salsa extra", 
            "quantity": 30, 
            "unit": "porción", 
            "price": 2000, 
            "descripcion": "Porción adicional de salsa Go Papa",
            "tipo_producto": "adicion"
        }
    ]
    
    # Add each menu item to the inventory
    for item in menu_items:
        result = await inventory_manager.add_product(
            restaurant_id=restaurant_id,
            name=item["name"],
            quantity=item["quantity"],
            unit=item["unit"],
            price=item["price"],
            descripcion=item.get("descripcion", ""),
            tipo_producto=item.get("tipo_producto", "menu")
        )
        
        if result:
            print(f"Added {item['name']} to inventory")
        else:
            print(f"Failed to add {item['name']} to inventory")

if __name__ == "__main__":
    asyncio.run(add_go_papa_menu_items())