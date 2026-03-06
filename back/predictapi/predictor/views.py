import io
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .ml_service import predict_product_seller, predict_service_seller


class PredictView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        seller_type = request.data.get('type')  # 'produit' or 'service'

        if not file:
            return Response({'error': 'Aucun fichier fourni.'}, status=status.HTTP_400_BAD_REQUEST)

        if not seller_type or seller_type not in ['produit', 'service']:
            return Response({'error': 'Type invalide. Choisissez "produit" ou "service".'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            content = file.read()
            # Try different separators
            for sep in [',', ';', '\t']:
                try:
                    df = pd.read_csv(io.BytesIO(content), sep=sep)
                    if len(df.columns) >= 3:
                        break
                except Exception:
                    continue

            if df.empty or len(df) < 3:
                return Response({'error': 'Le fichier CSV est vide ou insuffisant (minimum 3 lignes).'}, status=status.HTTP_400_BAD_REQUEST)

            if seller_type == 'produit':
                result = predict_product_seller(df)
            else:
                result = predict_service_seller(df)

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'Erreur de traitement: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
