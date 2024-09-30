CREATE TABLE clientes (
    id_cliente INT PRIMARY KEY,
    nombre VARCHAR(100),
    email VARCHAR(100),
    fecha_registro DATE
);

INSERT INTO clientes (id_cliente, nombre, email, fecha_registro) VALUES
(1, 'Juan Pérez', 'juan.perez@example.com', '2023-01-15'),
(2, 'Ana López', 'ana.lopez@example.com', '2023-02-20'),
(3, 'Carlos García', 'carlos.garcia@example.com', '2023-03-10'),
(4, 'María Fernández', 'maria.fernandez@example.com', '2023-04-05'),
(5, 'Luis Gómez', 'luis.gomez@example.com', '2023-05-18');

CREATE TABLE productos (
    id_producto INT PRIMARY KEY,
    nombre_producto VARCHAR(100),
    precio DECIMAL(10, 2),
    stock INT
);

INSERT INTO productos (id_producto, nombre_producto, precio, stock) VALUES
(101, 'Laptop', 750.00, 10),
(102, 'Smartphone', 500.00, 25),
(103, 'Tablet', 300.00, 15),
(104, 'Auriculares', 50.00, 100),
(105, 'Teclado', 30.00, 60);


CREATE TABLE ventas (
    id_venta INT PRIMARY KEY,
    id_cliente INT,
    id_producto INT,
    cantidad INT,
    fecha_venta DATE,
    total DECIMAL(10, 2),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);


INSERT INTO ventas (id_venta, id_cliente, id_producto, cantidad, fecha_venta, total) VALUES
(1, 1, 101, 1, '2023-06-10', 750.00),
(2, 2, 102, 2, '2023-06-12', 1000.00),
(3, 1, 103, 1, '2023-06-15', 300.00),
(4, 3, 104, 3, '2023-06-20', 150.00),
(5, 4, 105, 5, '2023-06-25', 150.00);

