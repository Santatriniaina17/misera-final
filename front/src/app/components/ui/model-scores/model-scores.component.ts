import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressBarModule } from '@angular/material/progress-bar';

@Component({
  selector: 'app-model-scores',
  imports: [CommonModule, MatCardModule, MatChipsModule, MatProgressBarModule],
  templateUrl: './model-scores.component.html',
  styleUrl: './model-scores.component.scss',
})
export class ModelScoresComponent {
  @Input() allScores: Record<string, number | null> = {};
  @Input() bestModel: string = '';
  @Input() bestScore: number = 0;

  get scores() {
    return Object.entries(this.allScores)
      .map(([name, score]) => ({ name, score }))
      .sort((a, b) => (b.score ?? -999) - (a.score ?? -999));
  }

  formatModelName(name: string): string {
    const map: Record<string, string> = {
      ridge: 'Ridge Regression',
      lasso: 'Lasso Regression',
      random_forest: 'Random Forest',
      gradient_boosting: 'Gradient Boosting',
      svr: 'SVR (SVM)',
      xgboost: '⚡ XGBoost',
    };
    return map[name] || name;
  }

  getBarValue(score: number | null): number {
    if (score === null) return 0;
    return Math.max(0, Math.min(100, score * 100));
  }
}
