import { Component, Input } from '@angular/core';
import { PredictionResult } from '../../../models/prediction.model';
import {
  MatCard,
  MatCardHeader,
  MatCardTitle,
  MatCardContent,
  MatCardSubtitle,
} from '@angular/material/card';
import { NgApexchartsModule } from 'ng-apexcharts';
import { ModelScoresComponent } from '../model-scores/model-scores.component';
import { ProductAnalysisComponent } from '../product-analysis/product-analysis.component';
import { ScoreBadgeComponent } from '../score-badge/score-badge.component';

@Component({
  selector: 'app-results',
  imports: [
    MatCard,
    MatCardHeader,
    MatCardTitle,
    MatCardContent,
    MatCardSubtitle,
    NgApexchartsModule,
    ModelScoresComponent,
    ProductAnalysisComponent,
    ScoreBadgeComponent,
  ],
  templateUrl: './results.component.html',
  styleUrl: './results.component.scss',
})
export class ResultsComponent {
  @Input() result!: PredictionResult;

  mainChartSeries: any[] = [];
  revDepSeries: any[] = [];
  productSeries: any[] = [];

  mainChartOptions: any = {
    chart: {
      type: 'area',
      height: 380,
      toolbar: { show: true },
      fontFamily: 'inherit',
    },
    stroke: { curve: 'smooth', width: [2, 3] },
    fill: {
      type: ['gradient', 'gradient'],
      gradient: {
        shadeIntensity: 0.5,
        opacityFrom: 0.4,
        opacityTo: 0.05,
        stops: [0, 90, 100],
      },
    },
    markers: { size: 4 },
    xaxis: { type: 'category', labels: { rotate: -30 } },
    yaxis: {
      title: { text: 'Bénéfice (Ar)' },
      labels: { formatter: (v: number) => `${v.toFixed(0)} Ar` },
    },
    tooltip: { y: { formatter: (v: number) => `${v.toFixed(0)} Ar` } },
    annotations: {},
    theme: { mode: 'light', palette: 'palette1' },
    grid: { borderColor: '#f0f0f0' },
  };

  barChartOptions: any = {
    chart: {
      type: 'bar',
      height: 300,
      toolbar: { show: false },
      fontFamily: 'inherit',
    },
    plotOptions: { bar: { borderRadius: 4, columnWidth: '60%' } },
    dataLabels: { enabled: false },
    xaxis: { type: 'category', labels: { rotate: -30 } },
    colors: ['#1dd1a1', '#ff6b6b'],
  };

  ngOnChanges() {
    if (!this.result) return;
    this.buildMainChart();
    if (this.result.type === 'service') this.buildRevDepChart();
    if (this.result.type === 'produit') this.buildProductChart();
  }

  private buildMainChart() {
    const historicalDates = this.result.historical.map((h) => h.date);
    const historicalValues = this.result.historical.map((h) => h.benefice);
    const predDates = this.result.predictions.map((p) => p.date);
    const predValues = this.result.predictions.map((p) => p.benefice);

    this.mainChartSeries = [
      {
        name: 'Historique',
        data: historicalDates.map((d, i) => ({ x: d, y: historicalValues[i] })),
        color: '#667eea',
      },
      {
        name: 'Prédictions',
        data: predDates.map((d, i) => ({ x: d, y: predValues[i] })),
        color: '#f7b731',
      },
    ];

    // Annotation line between historical and predictions
    if (predDates.length > 0) {
      this.mainChartOptions = {
        ...this.mainChartOptions,
        annotations: {
          xaxis: [
            {
              x: predDates[0],
              borderColor: '#f7b731',
              borderWidth: 2,
              strokeDashArray: 6,
              label: {
                text: 'Prédictions →',
                style: { background: '#f7b731', color: '#333' },
              },
            },
          ],
        },
      };
    }
  }

  private buildRevDepChart() {
    const dates = this.result.historical.map((h) => h.date);
    this.revDepSeries = [
      {
        name: 'Revenus',
        data: this.result.historical.map((h) => h.revenu ?? 0),
      },
      {
        name: 'Dépenses',
        data: this.result.historical.map((h) => h.depense ?? 0),
      },
    ];
    this.barChartOptions = {
      ...this.barChartOptions,
      xaxis: { ...this.barChartOptions.xaxis, categories: dates },
    };
  }

  private buildProductChart() {
    const dates = this.result.historical.map((h) => h.date);
    this.productSeries = [
      { name: 'CA', data: this.result.historical.map((h) => h.ca ?? 0) },
      { name: 'Coût', data: this.result.historical.map((h) => h.cout ?? 0) },
      { name: 'Bénéfice', data: this.result.historical.map((h) => h.benefice) },
    ];
    this.barChartOptions = {
      ...this.barChartOptions,
      xaxis: { ...this.barChartOptions.xaxis, categories: dates },
    };
  }
}
