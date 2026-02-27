import { Component, Input } from '@angular/core';
import { ScoreDetails, ScoreLabel } from '../../../models/prediction.model';

@Component({
  selector: 'app-score-badge',
  imports: [],
  templateUrl: './score-badge.component.html',
  styleUrl: './score-badge.component.scss',
})
export class ScoreBadgeComponent {
  @Input() score: ScoreLabel = 'moyen';
  @Input() details?: import('../../../models/prediction.model').ScoreDetails;

  get icon(): string {
    return { faible: '⚠️', moyen: '📊', élevé: '🚀' }[this.score] || '📊';
  }

  getPredClass(val: number): string {
    if (!this.details) return '';
    if (val >= this.details.historical_p66) return 'positive';
    if (val >= this.details.historical_p33) return 'neutral';
    return 'negative';
  }

  /** Positionne le marqueur en % sur la barre [0 → min historique, 100 → max] */
  getMarkerPos(val: number): number {
    if (!this.details) return 50;
    // On utilise p33 comme 33% et p66 comme 66% de la barre
    // Extension de plage : min = p33 - (p66-p33), max = p66 + (p66-p33)
    const range = this.details.historical_p66 - this.details.historical_p33;
    const min = this.details.historical_p33 - range;
    const max = this.details.historical_p66 + range;
    const pos = ((val - min) / (max - min)) * 100;
    return Math.max(2, Math.min(98, pos));
  }
}
