import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ModelScoresComponent } from './model-scores.component';

describe('ModelScoresComponent', () => {
  let component: ModelScoresComponent;
  let fixture: ComponentFixture<ModelScoresComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ModelScoresComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ModelScoresComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
