from rest_framework.views import APIView
from rest_framework.response import Response
from utils import logger
from .models import Account, AccountRequest, Card, CardRequest
from .serializers import (AccountSerializer, 
                          AccountRequestSerializer, 
                          CardSerializer, 
                          CardRequestSerializer
                          )

from users.models import CustomUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate


class AccountViewSet(ModelViewSet):
    """Viewset for Account model"""
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Account POST method"""
        if self.request.user.type == "CUSTOMER":
            return Response({"error": "Only bankers or admins can create accounts."}, status=403)

        try:
            serializer.save()
            return Response(serializer.data, status=201)
        except ValidationError as e:
            return Response({"error": "Couldn't validate"}, status=400)
        except Exception as e:
            logger('ACCOUNTS').info(f"Account creation problem")
            return Response({"error": "Something went wrong"}, status=500)
            
    def get_queryset(self):
        """GET, PUT, DELETE methods for Account"""
        try:
            if self.request.user.type in ["ADMIN", "BANKER"]:
                return Account.objects.all()
            user = self.request.user
            accounts = Account.objects.filter(user=user)
            if accounts.exists():
                return accounts
            raise Account.DoesNotExist
        except Exception as e:
            logger('ACCOUNTS').error(f"Error: {str(e)}")
            return Card.objects.none()
        
class CardViewSet(ModelViewSet):
    """Viewset for Card model"""
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Card POST method"""
        try:
            if self.request.user.type == "CUSTOMER":
                return Response({"error": "Only bankers or admins can create accounts."}, status=403)
        
            serializer.save()
            return Response(serializer.data, status=201)
        except ValidationError as e:
            return Response({"error": "Couldn't validate"}, status=400)
        except Exception as e:
            logger('ACCOUNTS').info(f"Card creation problem")
            return Response({"error": "Something went wrong"}, status=500)
            
    def get_queryset(self):
        """GET, PUT, DELETE methods for Card"""
        try:
            if self.request.user.type in ["ADMIN", "BANKER"]:
                return Card.objects.all()
            user = self.request.user
            cards = Card.objects.filter(user=user)
            if cards.exists():
                return cards
            raise Card.DoesNotExist
        except Exception as e:
            logger('ACCOUNTS').error(f"Error: {str(e)}")
            return Card.objects.none()
        

class AccountRequestViewSet(ModelViewSet):
    """Viewset for AccountRequest model"""
    queryset = AccountRequest.objects.all()
    serializer_class = AccountRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """AccountRequest POST method"""
        try:
            serializer.save()
            return Response(serializer.data, status=201)
        except ValidationError as e:
            return Response({"error": "Couldn't validate"}, status=400)
        except Exception as e:
            logger('ACCOUNTS').info(f"Account request creation problem")
            return Response({"error": "Something went wrong"}, status=500)
            
    def get_queryset(self):
        """GET, PUT, DELETE methods for AccountRequest"""
        try:
            if self.request.user.type == "CUSTOMER":
                return AccountRequest.objects.filter(user=self.request.user)
            account_request = AccountRequest.objects.all()
            if account_request.exists():
                return account_request
            raise AccountRequest.DoesNotExist
        except ValidationError as e:
            return Response({"error": "Couldn't validate"}, status=400)
        except Exception as e:
            logger('ACCOUNTS').error(f"Error: {str(e)}")
            return AccountRequest.objects.none()

class CardRequestViewSet(ModelViewSet):
    """Viewset for CardRequest model"""
    queryset = CardRequest.objects.all()
    serializer_class = CardRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """CardRequest POST method"""
        try:
            serializer.save()
            return Response(serializer.data, status=201)
        except ValidationError as e:
            return Response({"error": "Couldn't validate"}, status=400)
        except Exception as e:
            print(e)
            logger('ACCOUNTS').info(f"Card request creation problem")
            return Response({"error": "Something went wrong"}, status=500)
            
    def get_queryset(self):
        """GET DELETE methods for CardRequest"""
        try:
            card_request = CardRequest.objects.all()
            if card_request.exists():
                return card_request
            raise CardRequest.DoesNotExist
        except Exception as e:
            logger('ACCOUNTS').error(f"Error: {str(e)}")
            return CardRequest.objects.none()
        

class ApproveAccountRequestView(APIView):
    """Approve account request"""
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        """POST method for approving account request"""
        print(self.request.user.type)
        if self.request.user.type == "CUSTOMER":
            return Response({"error": "Only bankers or admins can approve card requests."}, status=403)
        
        try:
            account_request = AccountRequest.objects.get(pk=id, status='PENDING')
            account_request.approve() 
            return Response({"message": "Account request approved."}, status=200)
        except AccountRequest.DoesNotExist:
            return Response({"error": "Account request not found or already processed."}, status=404)
        except ValidationError as e:
            return Response({"error": "Couldn't validate"}, status=400)
        except Exception as e:
            logger('ACCOUNTS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
        
class RejectAccountRequestView(APIView):
    """Reject account request"""
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        """POST method for rejecting account request"""
        if self.request.user.type == "CUSTOMER":
            return Response({"error": "Only bankers or admins can approve card requests."}, status=403)
        
        try:
            account_request = AccountRequest.objects.get(pk=id, status='PENDING')
            account_request.reject(request.data.get('description', ''))
            return Response({"message": "Account request rejected."}, status=200)
        except AccountRequest.DoesNotExist:
            return Response({"error": "Account request not found or already processed."}, status=404)
        except ValidationError as e:
            return Response({"error": "Couldn't validate"}, status=400)
        except Exception as e:
            logger('ACCOUNTS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
        

class ApproveCardRequestView(APIView):
    """Approve card request"""
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        """POST method for approving card request"""
        if self.request.user.type == "CUSTOMER":
            return Response({"error": "Only bankers or admins can approve card requests."}, status=403)

        try:
            card_request = CardRequest.objects.get(pk=id, status='PENDING')
            card_request.approve() 
            return Response({"message": "Card request approved."}, status=200)
        except CardRequest.DoesNotExist:
            return Response({"error": "Card request not found or already processed."}, status=404)
        except ValidationError as e:
            return Response({"error": "Couldn't validate"}, status=400)
        except Exception as e:
            logger('ACCOUNTS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)
    
class RejectCardRequestView(APIView):
    """Reject card request"""
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        """POST method for rejecting card request"""
        if self.request.user.type == "CUSTOMER":
            return Response({"error": "Only bankers or admins can approve card requests."}, status=403)
        
        try:
            card_request = CardRequest.objects.get(pk=id, status='PENDING')
            card_request.reject(request.data.get('description', ''))
            return Response({"message": "Card request rejected."}, status=200)
        except CardRequest.DoesNotExist:
            return Response({"error": "Card request not found or already processed."}, status=404)
        except ValidationError as e:
            return Response({"error": "Couldn't validate"}, status=400)
        except Exception as e:
            logger('ACCOUNTS').error(f"Error: {str(e)}")
            return Response({"error": "Something went wrong"}, status=500)