import json

sql_script = """
-- Eliminar tablas si existen (en orden correcto por dependencias)
DROP TABLE IF EXISTS comunas CASCADE;
DROP TABLE IF EXISTS provincias CASCADE;
DROP TABLE IF EXISTS regiones CASCADE;

-- Crear tabla de regiones (solo id y nombre)
CREATE TABLE regiones (
id_region INT PRIMARY KEY,
nombre_region VARCHAR(100) NOT NULL UNIQUE
);

-- Crear tabla de provincias
CREATE TABLE provincias (
id_provincia INT PRIMARY KEY,
nombre_provincia VARCHAR(100) NOT NULL,
id_region INT NOT NULL REFERENCES regiones(id_region),
UNIQUE (nombre_provincia, id_region)
);

-- Crear tabla de comunas (solo id, nombre y id_provincia)
CREATE TABLE comunas (
id_comuna INT PRIMARY KEY,
nombre_comuna VARCHAR(100) NOT NULL,
id_provincia INT NOT NULL REFERENCES provincias(id_provincia),
UNIQUE (nombre_comuna, id_provincia)
);

-- Insertar regiones (solo id y nombre)
INSERT INTO regiones (id_region, nombre_region) VALUES
(15, 'Arica y Parinacota'),
(1, 'Tarapacá'),
(2, 'Antofagasta'),
(3, 'Atacama'),
(4, 'Coquimbo'),
(5, 'Valparaíso'),
(13, 'Metropolitana de Santiago'),
(6, 'Libertador General Bernardo O''Higgins'),
(7, 'Maule'),
(16, 'Ñuble'),
(8, 'Biobío'),
(9, 'La Araucanía'),
(14, 'Los Ríos'),
(10, 'Los Lagos'),
(11, 'Aysén del General Carlos Ibáñez del Campo'),
(12, 'Magallanes y de la Antártica Chilena');

-- Insertar provincias
INSERT INTO provincias (id_provincia, nombre_provincia, id_region) VALUES
-- Arica y Parinacota (15)
(151, 'Arica', 15),
(152, 'Parinacota', 15),

-- Tarapacá (1)
(11, 'Iquique', 1),
(14, 'Tamarugal', 1),

-- Antofagasta (2)
(21, 'Antofagasta', 2),
(22, 'El Loa', 2),
(23, 'Tocopilla', 2),

-- Atacama (3)
(31, 'Copiapó', 3),
(32, 'Chañaral', 3),
(33, 'Huasco', 3),

-- Coquimbo (4)
(41, 'Elqui', 4),
(42, 'Choapa', 4),
(43, 'Limarí', 4),

-- Valparaíso (5)
(51, 'Valparaíso', 5),
(52, 'Isla de Pascua', 5),
(53, 'Los Andes', 5),
(54, 'Petorca', 5),
(55, 'Quillota', 5),
(56, 'San Antonio', 5),
(57, 'San Felipe de Aconcagua', 5),
(58, 'Marga Marga', 5),

-- Metropolitana (13)
(131, 'Santiago', 13),
(132, 'Cordillera', 13),
(133, 'Chacabuco', 13),
(134, 'Maipo', 13),
(135, 'Melipilla', 13),
(136, 'Talagante', 13),

-- O'Higgins (6)
(61, 'Cachapoal', 6),
(62, 'Cardenal Caro', 6),
(63, 'Colchagua', 6),

-- Maule (7)
(71, 'Talca', 7),
(72, 'Cauquenes', 7),
(73, 'Curicó', 7),
(74, 'Linares', 7),

-- Ñuble (16)
(161, 'Diguillín', 16),
(162, 'Itata', 16),
(163, 'Punilla', 16),

-- Biobío (8)
(81, 'Concepción', 8),
(82, 'Arauco', 8),
(83, 'Biobío', 8),

-- Araucanía (9)
(91, 'Cautín', 9),
(92, 'Malleco', 9),

-- Los Ríos (14)
(141, 'Valdivia', 14),
(142, 'Ranco', 14),

-- Los Lagos (10)
(101, 'Llanquihue', 10),
(102, 'Chiloé', 10),
(103, 'Osorno', 10),
(104, 'Palena', 10),

-- Aysén (11)
(111, 'Coyhaique', 11),
(112, 'Aysén', 11),
(113, 'Capitán Prat', 11),
(114, 'General Carrera', 11),

-- Magallanes (12)
(121, 'Magallanes', 12),
(122, 'Antártica Chilena', 12),
(123, 'Tierra del Fuego', 12),
(124, 'Última Esperanza', 12);

-- Insertar comunas (solo id, nombre y id_provincia)
INSERT INTO comunas (id_comuna, nombre_comuna, id_provincia) VALUES
-- Arica (151)
(15101, 'Arica', 151),
(15102, 'Camarones', 151),

-- Parinacota (152)
(15201, 'Putre', 152),
(15202, 'General Lagos', 152),

-- Iquique (11)
(1101, 'Iquique', 11),
(1107, 'Alto Hospicio', 11),

-- Tamarugal (14)
(1401, 'Pozo Almonte', 14),
(1402, 'Camiña', 14),
(1403, 'Colchane', 14),
(1404, 'Huara', 14),
(1405, 'Pica', 14),

-- Antofagasta (21)
(2101, 'Antofagasta', 21),
(2102, 'Mejillones', 21),
(2103, 'Sierra Gorda', 21),
(2104, 'Taltal', 21),

-- El Loa (22)
(2201, 'Calama', 22),
(2202, 'Ollagüe', 22),
(2203, 'San Pedro de Atacama', 22),

-- Tocopilla (23)
(2301, 'Tocopilla', 23),
(2302, 'María Elena', 23),

-- Copiapó (31)
(3101, 'Copiapó', 31),
(3102, 'Caldera', 31),
(3103, 'Tierra Amarilla', 31),

-- Chañaral (32)
(3201, 'Chañaral', 32),
(3202, 'Diego de Almagro', 32),

-- Huasco (33)
(3301, 'Vallenar', 33),
(3302, 'Alto del Carmen', 33),
(3303, 'Freirina', 33),
(3304, 'Huasco', 33),

-- Elqui (41)
(4101, 'La Serena', 41),
(4102, 'Coquimbo', 41),
(4103, 'Andacollo', 41),
(4104, 'La Higuera', 41),
(4105, 'Vicuña', 41),
(4106, 'Paihuano', 41),

-- Limarí (43)
(4301, 'Ovalle', 43),
(4302, 'Río Hurtado', 43),
(4303, 'Monte Patria', 43),
(4304, 'Combarbalá', 43),
(4305, 'Punitaqui', 43),

-- Choapa (42)
(4201, 'Illapel', 42),
(4202, 'Salamanca', 42),
(4203, 'Los Vilos', 42),
(4204, 'Canela', 42),

-- Valparaíso (51)
(5101, 'Valparaíso', 51),
(5102, 'Viña del Mar', 51),
(5103, 'Concón', 51),
(5104, 'Quintero', 51),
(5105, 'Puchuncaví', 51),
(5106, 'Casablanca', 51),
(5107, 'Juan Fernández', 51),

-- Isla de Pascua (52)
(5201, 'Isla de Pascua', 52),

-- Los Andes (53)
(5301, 'Los Andes', 53),
(5302, 'San Esteban', 53),
(5303, 'Calle Larga', 53),
(5304, 'Rinconada', 53),

-- Petorca (54)
(5401, 'La Ligua', 54),
(5402, 'Cabildo', 54),
(5403, 'Papudo', 54),
(5404, 'Petorca', 54),
(5405, 'Zapallar', 54),

-- Quillota (55)
(5501, 'Quillota', 55),
(5502, 'La Calera', 55),
(5503, 'Hijuelas', 55),
(5504, 'La Cruz', 55),
(5505, 'Nogales', 55),

-- San Antonio (56)
(5601, 'San Antonio', 56),
(5602, 'Cartagena', 56),
(5603, 'El Tabo', 56),
(5604, 'El Quisco', 56),
(5605, 'Algarrobo', 56),
(5606, 'Santo Domingo', 56),

-- San Felipe de Aconcagua (57)
(5701, 'San Felipe', 57),
(5702, 'Llaillay', 57),
(5703, 'Putaendo', 57),
(5704, 'Santa María', 57),
(5705, 'Catemu', 57),
(5706, 'Panquehue', 57),

-- Marga Marga (58)
(5801, 'Quilpué', 58),
(5802, 'Limache', 58),
(5803, 'Villa Alemana', 58),
(5804, 'Olmué', 58),

-- Santiago (131)
(13101, 'Santiago', 131),
(13102, 'Cerrillos', 131),
(13103, 'Cerro Navia', 131),
(13104, 'Conchalí', 131),
(13105, 'El Bosque', 131),
(13106, 'Estación Central', 131),
(13107, 'Huechuraba', 131),
(13108, 'Independencia', 131),
(13109, 'La Cisterna', 131),
(13110, 'La Florida', 131),
(13111, 'La Granja', 131),
(13112, 'La Pintana', 131),
(13113, 'La Reina', 131),
(13114, 'Las Condes', 131),
(13115, 'Lo Barnechea', 131),
(13116, 'Lo Espejo', 131),
(13117, 'Lo Prado', 131),
(13118, 'Macul', 131),
(13119, 'Maipú', 131),
(13120, 'Ñuñoa', 131),
(13121, 'Pedro Aguirre Cerda', 131),
(13122, 'Peñalolén', 131),
(13123, 'Providencia', 131),
(13124, 'Pudahuel', 131),
(13125, 'Quilicura', 131),
(13126, 'Quinta Normal', 131),
(13127, 'Recoleta', 131),
(13128, 'Renca', 131),
(13129, 'San Joaquín', 131),
(13130, 'San Miguel', 131),
(13131, 'San Ramón', 131),
(13132, 'Vitacura', 131),
(13133, 'Puente Alto', 131),
(13134, 'Pirque', 131),
(13135, 'San José de Maipo', 131),

-- Cordillera (132)
(13201, 'Colina', 132),
(13202, 'Lampa', 132),
(13203, 'Tiltil', 132),

-- Chacabuco (133)
(13301, 'Paine', 133),
(13302, 'Buin', 133),
(13303, 'Calera de Tango', 133),
(13304, 'San Bernardo', 133),

-- Maipo (134)
(13401, 'Talagante', 134),
(13402, 'Peñaflor', 134),
(13403, 'Isla de Maipo', 134),
(13404, 'El Monte', 134),
(13405, 'Padre Hurtado', 134),

-- Melipilla (135)
(13501, 'Melipilla', 135),
(13502, 'Curacaví', 135),
(13503, 'María Pinto', 135),
(13504, 'San Pedro', 135),
(13505, 'Alhué', 135),

-- Talagante (136)
(13601, 'Talagante', 136),
(13602, 'Peñaflor', 136),
(13603, 'Isla de Maipo', 136),
(13604, 'El Monte', 136),
(13605, 'Padre Hurtado', 136),

-- Cachapoal (61)
(6101, 'Rancagua', 61),
(6102, 'Codegua', 61),
(6103, 'Coinco', 61),
(6104, 'Coltauco', 61),
(6105, 'Doñihue', 61),
(6106, 'Graneros', 61),
(6107, 'Las Cabras', 61),
(6108, 'Machalí', 61),
(6109, 'Malloa', 61),
(6110, 'Mostazal', 61),
(6111, 'Olivar', 61),
(6112, 'Peumo', 61),
(6113, 'Pichidegua', 61),
(6114, 'Quinta de Tilcoco', 61),
(6115, 'Rengo', 61),
(6116, 'Requínoa', 61),
(6117, 'San Vicente', 61),

-- Cardenal Caro (62)
(6201, 'Pichilemu', 62),
(6202, 'La Estrella', 62),
(6203, 'Litueche', 62),
(6204, 'Marchihue', 62),
(6205, 'Navidad', 62),
(6206, 'Paredones', 62),

-- Colchagua (63)
(6301, 'San Fernando', 63),
(6302, 'Chépica', 63),
(6303, 'Chimbarongo', 63),
(6304, 'Lolol', 63),
(6305, 'Nancagua', 63),
(6306, 'Palmilla', 63),
(6307, 'Peralillo', 63),
(6308, 'Placilla', 63),
(6309, 'Pumanque', 63),
(6310, 'Santa Cruz', 63),

-- Talca (71)
(7101, 'Talca', 71),
(7102, 'Constitución', 71),
(7103, 'Curepto', 71),
(7104, 'Empedrado', 71),
(7105, 'Maule', 71),
(7106, 'Pelarco', 71),
(7107, 'Pencahue', 71),
(7108, 'Río Claro', 71),
(7109, 'San Clemente', 71),
(7110, 'San Rafael', 71),

-- Cauquenes (72)
(7201, 'Cauquenes', 72),
(7202, 'Chanco', 72),
(7203, 'Pelluhue', 72),

-- Curicó (73)
(7301, 'Curicó', 73),
(7302, 'Hualañé', 73),
(7303, 'Licantén', 73),
(7304, 'Molina', 73),
(7305, 'Rauco', 73),
(7306, 'Romeral', 73),
(7307, 'Sagrada Familia', 73),
(7308, 'Teno', 73),
(7309, 'Vichuquén', 73),

-- Linares (74)
(7401, 'Linares', 74),
(7402, 'Colbún', 74),
(7403, 'Longaví', 74),
(7404, 'Parral', 74),
(7405, 'Retiro', 74),
(7406, 'San Javier', 74),
(7407, 'Villa Alegre', 74),
(7408, 'Yerbas Buenas', 74),

-- Diguillín (161)
(16101, 'Chillán', 161),
(16102, 'Bulnes', 161),
(16103, 'Chillán Viejo', 161),
(16104, 'El Carmen', 161),
(16105, 'Pemuco', 161),
(16106, 'Pinto', 161),
(16107, 'Quillón', 161),
(16108, 'San Ignacio', 161),
(16109, 'Yungay', 161),

-- Itata (162)
(16201, 'Quirihue', 162),
(16202, 'Cobquecura', 162),
(16203, 'Coelemu', 162),
(16204, 'Ninhue', 162),
(16205, 'Portezuelo', 162),
(16206, 'Ránquil', 162),
(16207, 'Treguaco', 162),

-- Punilla (163)
(16301, 'San Carlos', 163),
(16302, 'Coihueco', 163),
(16303, 'Ñiquén', 163),
(16304, 'San Fabián', 163),
(16305, 'San Nicolás', 163),

-- Concepción (81)
(8101, 'Concepción', 81),
(8102, 'Coronel', 81),
(8103, 'Chiguayante', 81),
(8104, 'Florida', 81),
(8105, 'Hualqui', 81),
(8106, 'Lota', 81),
(8107, 'Penco', 81),
(8108, 'San Pedro de la Paz', 81),
(8109, 'Santa Juana', 81),
(8110, 'Talcahuano', 81),
(8111, 'Tomé', 81),
(8112, 'Hualpén', 81),

-- Arauco (82)
(8201, 'Lebu', 82),
(8202, 'Arauco', 82),
(8203, 'Cañete', 82),
(8204, 'Contulmo', 82),
(8205, 'Curanilahue', 82),
(8206, 'Los Álamos', 82),
(8207, 'Tirúa', 82),

-- Biobío (83)
(8301, 'Los Ángeles', 83),
(8302, 'Antuco', 83),
(8303, 'Cabrero', 83),
(8304, 'Laja', 83),
(8305, 'Mulchén', 83),
(8306, 'Nacimiento', 83),
(8307, 'Negrete', 83),
(8308, 'Quilaco', 83),
(8309, 'Quilleco', 83),
(8310, 'San Rosendo', 83),
(8311, 'Santa Bárbara', 83),
(8312, 'Tucapel', 83),
(8313, 'Yumbel', 83),
(8314, 'Alto Biobío', 83),

-- Cautín (91)
(9101, 'Temuco', 91),
(9102, 'Carahue', 91),
(9103, 'Cunco', 91),
(9104, 'Curarrehue', 91),
(9105, 'Freire', 91),
(9106, 'Galvarino', 91),
(9107, 'Gorbea', 91),
(9108, 'Lautaro', 91),
(9109, 'Loncoche', 91),
(9110, 'Melipeuco', 91),
(9111, 'Nueva Imperial', 91),
(9112, 'Padre las Casas', 91),
(9113, 'Perquenco', 91),
(9114, 'Pitrufquén', 91),
(9115, 'Pucón', 91),
(9116, 'Saavedra', 91),
(9117, 'Teodoro Schmidt', 91),
(9118, 'Toltén', 91),
(9119, 'Vilcún', 91),
(9120, 'Villarrica', 91),
(9121, 'Cholchol', 91),

-- Malleco (92)
(9201, 'Angol', 92),
(9202, 'Collipulli', 92),
(9203, 'Curacautín', 92),
(9204, 'Ercilla', 92),
(9205, 'Lonquimay', 92),
(9206, 'Los Sauces', 92),
(9207, 'Lumaco', 92),
(9208, 'Purén', 92),
(9209, 'Renaico', 92),
(9210, 'Traiguén', 92),
(9211, 'Victoria', 92),

-- Valdivia (141)
(14101, 'Valdivia', 141),
(14102, 'Corral', 141),
(14103, 'Lanco', 141),
(14104, 'Los Lagos', 141),
(14105, 'Máfil', 141),
(14106, 'Mariquina', 141),
(14107, 'Paillaco', 141),
(14108, 'Panguipulli', 141),
(14109, 'Río Bueno', 141),

-- Ranco (142)
(14201, 'La Unión', 142),
(14202, 'Futrono', 142),
(14203, 'Lago Ranco', 142),

-- Llanquihue (101)
(10101, 'Puerto Montt', 101),
(10102, 'Calbuco', 101),
(10103, 'Cochamó', 101),
(10104, 'Fresia', 101),
(10105, 'Frutillar', 101),
(10106, 'Los Muermos', 101),
(10107, 'Llanquihue', 101),
(10108, 'Maullín', 101),
(10109, 'Puerto Varas', 101),

-- Chiloé (102)
(10201, 'Castro', 102),
(10202, 'Ancud', 102),
(10203, 'Chonchi', 102),
(10204, 'Curaco de Vélez', 102),
(10205, 'Dalcahue', 102),
(10206, 'Puqueldón', 102),
(10207, 'Queilén', 102),
(10208, 'Quellón', 102),
(10209, 'Quemchi', 102),
(10210, 'Quinchao', 102),

-- Osorno (103)
(10301, 'Osorno', 103),
(10302, 'Puerto Octay', 103),
(10303, 'Purranque', 103),
(10304, 'Puyehue', 103),
(10305, 'Río Negro', 103),
(10306, 'San Juan de la Costa', 103),
(10307, 'San Pablo', 103),

-- Palena (104)
(10401, 'Chaitén', 104),
(10402, 'Futaleufú', 104),
(10403, 'Hualaihué', 104),
(10404, 'Palena', 104),

-- Coyhaique (111)
(11101, 'Coyhaique', 111),
(11102, 'Lago Verde', 111),

-- Aysén (112)
(11201, 'Aysén', 112),
(11202, 'Cisnes', 112),
(11203, 'Guaitecas', 112),

-- Capitán Prat (113)
(11301, 'Cochrane', 113),
(11302, 'O''Higgins', 113),
(11303, 'Tortel', 113),

-- General Carrera (114)
(11401, 'Chile Chico', 114),
(11402, 'Río Ibáñez', 114),

-- Magallanes (121)
(12101, 'Punta Arenas', 121),
(12102, 'Laguna Blanca', 121),
(12103, 'Río Verde', 121),
(12104, 'San Gregorio', 121),

-- Antártica Chilena (122)
(12201, 'Cabo de Hornos', 122),
(12202, 'Antártica', 122),

-- Tierra del Fuego (123)
(12301, 'Porvenir', 123),
(12302, 'Primavera', 123),
(12303, 'Timaukel', 123),

-- Última Esperanza (124)
(12401, 'Natales', 124),
(12402, 'Torres del Paine', 124);
"""

def parse_chile_sql_to_json(sql: str):
    regiones = {}
    provincias = {}
    comunas = []
    section = None

    for raw_line in sql.splitlines():
        line = raw_line.strip()

        # Detectar secciones
        if line.upper().startswith("INSERT INTO REGIONES"):
            section = "regiones"
            continue
        if line.upper().startswith("INSERT INTO PROVINCIAS"):
            section = "provincias"
            continue
        if line.upper().startswith("INSERT INTO COMUNAS"):
            section = "comunas"
            continue

        # Fin de sección
        if section and line.endswith(";"):
            section = None
            continue

        # Ignorar comentarios o líneas vacías
        if not line or line.startswith("--"):
            continue

        # Solo procesar tuplas (…)
        if not line.startswith("("):
            continue

        # Limpieza
        content = line.lstrip("(").rstrip(",);")
        parts = [p.strip() for p in content.split(",")]

        # Limpia strings con comillas, tildes, doble apóstrofe
        def clean_str(s: str) -> str:
            s = s.strip()
            if s.startswith("'") and s.endswith("'"):
                s = s[1:-1]
            return s.replace("''", "'")

        # REGIONES
        if section == "regiones":
            id_region = int(parts[0])
            nombre = clean_str(parts[1])
            regiones[id_region] = {
                "id_region": id_region,
                "nombre_region": nombre,
            }

        # PROVINCIAS
        elif section == "provincias":
            id_prov = int(parts[0])
            nombre = clean_str(parts[1])
            id_reg = int(parts[2])
            provincias[id_prov] = {
                "id_provincia": id_prov,
                "nombre_provincia": nombre,
                "id_region": id_reg,
            }

        # COMUNAS
        elif section == "comunas":
            id_com = int(parts[0])
            nombre = clean_str(parts[1])
            id_prov = int(parts[2])
            comunas.append({
                "id_comuna": id_com,
                "nombre_comuna": nombre,
                "id_provincia": id_prov,
            })

    # Construir árbol Región → Provincia → Comunas
    comunas_por_prov = {}
    for c in comunas:
        comunas_por_prov.setdefault(c["id_provincia"], []).append(c)

    provincias_por_region = {}
    for p in provincias.values():
        provincias_por_region.setdefault(p["id_region"], []).append(p)

    chile = []
    for id_region in sorted(regiones.keys()):
        reg = regiones[id_region]

        entry = {
            "id_region": reg["id_region"],
            "nombre_region": reg["nombre_region"],
            "provincias": []
        }

        for prov in sorted(provincias_por_region.get(id_region, []), key=lambda p: p["id_provincia"]):

            entry["provincias"].append({
                "id_provincia": prov["id_provincia"],
                "nombre_provincia": prov["nombre_provincia"],
                "comunas": sorted(
                    comunas_por_prov.get(prov["id_provincia"], []),
                    key=lambda c: c["id_comuna"]
                )
            })

        chile.append(entry)

    return chile


if __name__ == "__main__":
    data = parse_chile_sql_to_json(sql_script)
    json_output = json.dumps(data, ensure_ascii=False, indent=2)

    # Imprimir o guardar
    print(json_output)

    # Guardar en archivo
    with open("chile-regiones-2025.json", "w", encoding="utf-8") as f:
        f.write(json_output)