module.exports = {
  apps: [
    {
      name: 'servidor',           // Nombre de la aplicación en PM2
      script: 'main.py',      // Script que se ejecutará
      interpreter: 'python',      // Interprete para ejecutar el script (asegúrate de que python3 esté instalado)
      watch: false,               // Desactivar la observación de archivos para reinicios automáticos
      autorestart: true,          // Reiniciar automáticamente si la aplicación se cae
      max_restarts: 10,           // Número máximo de reinicios si la aplicación falla
      restart_delay: 5000,        // Espera de 5 segundos entre reinicios
      env: {
        NODE_ENV: 'production',   // Entorno de producción
      },
      env_development: {
        NODE_ENV: 'development',  // Entorno de desarrollo
      },
    },
  ],
};
