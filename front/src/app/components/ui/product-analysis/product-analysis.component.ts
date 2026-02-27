import { Component, Input } from '@angular/core';
import { ProductRecommendation } from '../../../models/prediction.model';

@Component({
  selector: 'app-product-analysis',
  imports: [],
  templateUrl: './product-analysis.component.html',
  styleUrl: './product-analysis.component.scss',
})
export class ProductAnalysisComponent {
  @Input() products: ProductRecommendation[] = [];

  displayedColumns = [
    'priorite',
    'designation',
    'total_ventes',
    'marge_pct',
    'prix_vente_moyen',
    'benefice_total',
    'approvisionnement_suggere',
  ];

  prioriteIcon(p: string): string {
    return { haute: '🔴', moyenne: '🟡', basse: '🟢' }[p] || '';
  }
}
