package com.example.poemasjava;

import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.Spinner;
import android.widget.TextView;
import com.example.poemasjava.PoemaUtils;

import java.io.IOException;
import java.util.List;

public class MainActivity extends AppCompatActivity {
    Button btnGenerarPoema, btnMostrarPoema;
    Spinner spinnerPoemas;
    TextView tvPoema;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        btnGenerarPoema = findViewById(R.id.btn_generar_poema);
        btnMostrarPoema = findViewById(R.id.btn_mostrar_poema);
        spinnerPoemas = findViewById(R.id.spinner_poemas);
        tvPoema = findViewById(R.id.tv_poema);

        // Cargar poemas y nombres
        try {
            PoemaUtils.cargarPoemas(this);
            configurarSpinner();
        } catch (IOException e) {
            tvPoema.setText("Error al cargar los poemas.");
            return;
        }

        // Configurar eventos de los botones
        btnGenerarPoema.setOnClickListener(v -> {
            String poema = PoemaUtils.generarPoemaAleatorio();
            tvPoema.setText(poema);
        });

        btnMostrarPoema.setOnClickListener(v -> {
            String nombreSeleccionado = spinnerPoemas.getSelectedItem().toString();
            String poema = PoemaUtils.buscarPoemaPorNombre(nombreSeleccionado);
            tvPoema.setText(poema);
        });
    }

    private void configurarSpinner() {
        // Obtener nombres de los poemas
        List<String> nombresPoemas = PoemaUtils.obtenerNombresPoemas();

        // Configurar el adaptador para el spinner
        ArrayAdapter<String> adapter = new ArrayAdapter<>(
                this,
                android.R.layout.simple_spinner_item,
                nombresPoemas
        );
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinnerPoemas.setAdapter(adapter);
    }
}
