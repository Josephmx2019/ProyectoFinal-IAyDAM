package com.example.poemasjava;

import android.content.Context;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

public class PoemaUtils {
    private static final Random rnd = new Random();
    private static final Map<String, List<String>> poemasPorNombre = new HashMap<>();
    private static final List<String> nombresPoemas = new ArrayList<>();

    /**
     * Carga los nombres y versos de los poemas desde los archivos en assets.
     */
    public static void cargarPoemas(Context context) throws IOException {
        // Cargar nombres de poemas
        try (BufferedReader nombresReader = new BufferedReader(
                new InputStreamReader(context.getAssets().open("nombres.txt")))) {
            String nombre;
            while ((nombre = nombresReader.readLine()) != null) {
                nombresPoemas.add(nombre.trim());
            }
        }

        // Cargar versos de los poemas y asociarlos a los nombres
        try (BufferedReader poemasReader = new BufferedReader(
                new InputStreamReader(context.getAssets().open("poemas.txt")))) {
            List<String> poemaActual = new ArrayList<>();
            int index = 0;

            String line;
            while ((line = poemasReader.readLine()) != null) {
                if (!line.trim().isEmpty()) {
                    poemaActual.add(line);
                } else {
                    if (!poemaActual.isEmpty() && index < nombresPoemas.size()) {
                        poemasPorNombre.put(nombresPoemas.get(index), new ArrayList<>(poemaActual));
                        poemaActual.clear();
                        index++;
                    }
                }
            }

            // Agregar el último poema si quedó pendiente
            if (!poemaActual.isEmpty() && index < nombresPoemas.size()) {
                poemasPorNombre.put(nombresPoemas.get(index), poemaActual);
            }
        }
    }

    /**
     * Genera un poema aleatorio combinando versos de distintos poemas.
     */
    public static String generarPoemaAleatorio() {
        // Verifica si hay poemas disponibles
        if (poemasPorNombre.isEmpty()) {
            return "No hay poemas disponibles.";
        }

        // Número de versos por poema (se usa el primer poema como referencia)
        int numVersos = poemasPorNombre.values().iterator().next().size();

        // Lista para almacenar el poema aleatorio
        List<String> poemaAleatorio = new ArrayList<>();

        // Generar poema
        for (int i = 0; i < numVersos; i++) {
            // Seleccionar un poema aleatorio
            List<String> nombres = new ArrayList<>(poemasPorNombre.keySet());
            String nombreAleatorio = nombres.get(rnd.nextInt(nombres.size()));
            List<String> poemaSeleccionado = poemasPorNombre.get(nombreAleatorio);

            // Obtener un verso aleatorio del poema seleccionado
            String versoAleatorio = poemaSeleccionado.get(i);

            // Numerar y agregar el verso al poema aleatorio
            String versoNumerado = (i + 1) + ". " + versoAleatorio;
            poemaAleatorio.add(versoNumerado);
        }

        // Crear párrafos de 4 versos cada uno
        StringBuilder poemaFormateado = new StringBuilder();
        for (int j = 0; j < numVersos; j += 4) {
            // Agrupar 4 versos en un párrafo
            for (int k = 0; k < 4 && j + k < numVersos; ++k) {
                poemaFormateado.append(poemaAleatorio.get(j + k)).append("\n");
            }
            poemaFormateado.append("\n");
        }

        return poemaFormateado.toString();
    }

    /**
     * Busca un poema por su nombre.
     */
    public static String buscarPoemaPorNombre(String nombre) {
        if (poemasPorNombre.containsKey(nombre)) {
            List<String> poema = poemasPorNombre.get(nombre);
            StringBuilder poemaFormateado = new StringBuilder();
            for (int i = 0; i < poema.size(); i++) {
                poemaFormateado.append((i + 1)).append(". ").append(poema.get(i)).append("\n");
            }
            return poemaFormateado.toString();
        }
        return "Poema no encontrado.";
    }

    /**
     * Devuelve una lista con los nombres de los poemas.
     */
    public static List<String> obtenerNombresPoemas() {
        return new ArrayList<>(nombresPoemas);
    }
}

