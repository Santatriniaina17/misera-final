import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProductAnalysisComponent } from './product-analysis.component';

describe('ProductAnalysisComponent', () => {
  let component: ProductAnalysisComponent;
  let fixture: ComponentFixture<ProductAnalysisComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProductAnalysisComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ProductAnalysisComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
