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

    ]
    
    # Adiciones de 10,000 pesos
    adiciones_10k = [
        {"name": "Chicharrón", "price": 10000, "descripcion": "Chicharrón crujiente para añadir a tu plato"},
        {"name": "Carne Mechada", "price": 10000, "descripcion": "Deliciosa carne mechada para complementar tu pedido"},
        {"name": "Costilla", "price": 10000, "descripcion": "Tierna costilla para añadir a tu plato"},
        {"name": "Salchicha", "price": 10000, "descripcion": "Salchicha adicional para tu plato"},
        {"name": "Pollo", "price": 10000, "descripcion": "Pollo adicional para complementar tu pedido"},
        {"name": "Queso Fundido", "price": 10000, "descripcion": "Delicioso queso fundido extra"},
        {"name": "Nuggets", "price": 10000, "descripcion": "Nuggets de pollo para complementar tu plato"},
        {"name": "Pulled Pork", "price": 10000, "descripcion": "Carne de cerdo desmenuzada y sazonada"},
        {"name": "Chorizo", "price": 10000, "descripcion": "Chorizo adicional para tu plato"},
        {"name": "Chorizo Español", "price": 10000, "descripcion": "Chorizo español importado para tu plato"},
        {"name": "Jamón Serrano", "price": 10000, "descripcion": "Jamón serrano para complementar tu pedido"},
        {"name": "Tocineta", "price": 10000, "descripcion": "Tocineta crujiente adicional"},
        {"name": "Salami", "price": 10000, "descripcion": "Salami para añadir a tu plato"}
    ]

    # Adiciones de 8,000 pesos
    adiciones_8k = [
        {"name": "Papa", "price": 8000, "descripcion": "Porción extra de papas"},
        {"name": "Piña Calada", "price": 8000, "descripcion": "Piña caramelizada para añadir un toque dulce"},
        {"name": "Pico e Gallo", "price": 8000, "descripcion": "Mezcla fresca de tomate, cebolla y cilantro"},
        {"name": "Guacamole", "price": 8000, "descripcion": "Guacamole fresco para complementar tu plato"},
        {"name": "Maduro Calado", "price": 8000, "descripcion": "Plátano maduro frito para añadir a tu plato"},
        {"name": "Maicitos", "price": 8000, "descripcion": "Maíz tierno para añadir a tu plato"},
        {"name": "Huevos de Codorniz", "price": 8000, "descripcion": "Huevos de codorniz para complementar tu plato"},
        {"name": "Cebolla Crispy", "price": 8000, "descripcion": "Cebolla crujiente para dar un toque especial"}
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

    # Agregar todas las adiciones al inventario
    for adicion in adiciones_10k + adiciones_8k:
        await inventory_manager.add_product(
            restaurant_id=restaurant_id,
            name=adicion["name"],
            quantity=100,  # Cantidad inicial en inventario
            unit="porción",
            price=adicion["price"],
            descripcion=adicion["descripcion"],
            tipo_producto="adicion"  # Importante: marcar como adición
        )
        print(f"Adición agregada: {adicion['name']} - ${adicion['price']}")

if __name__ == "__main__":
    asyncio.run(add_go_papa_menu_items())