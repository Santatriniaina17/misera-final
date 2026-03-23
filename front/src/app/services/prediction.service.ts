import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { PredictionResult, SellerType } from '../models/prediction.model';

@Injectable({
  providedIn: 'root',
})
export class PredictionService {
  //private apiUrl = 'http://127.0.0.1:8000/api/predict/';
  private apiUrl = 'https://misera-final.onrender.com/api/predict/';
  constructor(private http: HttpClient) {}
  predict(file: File, type: SellerType): Observable<PredictionResult> {
    const form = new FormData();
    form.append('file', file);
    form.append('type', type);
    return this.http.post<PredictionResult>(this.apiUrl, form);
  }
}
