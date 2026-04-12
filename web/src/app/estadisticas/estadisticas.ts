import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration,ChartData, ChartType } from 'chart.js';

@Component({
  selector: 'app-estadisticas',
  imports: [CommonModule, BaseChartDirective],
  templateUrl: './estadisticas.html',
  styleUrl: './estadisticas.css',
})

export class EstadisticasComponent {
  // Configuración de ejemplo
  public barChartOptions: ChartConfiguration['options'] = {
    responsive: true,
  };
  public barChartType: ChartType = 'bar';
  public barChartData: ChartData<'bar'> = {
    labels: ['CSV', 'PDF', 'XLS', 'JSON'],
    datasets: [
      { data: [65, 59, 80, 81], label: 'Formatos' }
    ]
  };
}
