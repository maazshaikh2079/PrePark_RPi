import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase-config/prepark-sap-firebase-adminsdk-bft4o-4aead8250d.json");
firebase_admin.initialize_app(cred);

db = firestore.client();

collection_name = "License_Plates";

docs = db.collection(collection_name).get()

vehicle=input("Enter Plate Number: ");

count = 0;

print();

if docs:
    print("All data in 'License_Plates' collection:")
    print("Documents :",docs);
    print();
    for doc in docs:
        count +=1
        print(f"Document {count} :",doc);
        plate=doc.to_dict();
        print(f"Plate {count} :",plate);
        value = list(plate.values());
        value = value[0];
        print(f"Value {count} :",value)
        if (value == vehicle):
            print(f"Comaparison {count} : Value == Vehicle No. : {value}(value)");
            print("[Registered vehicle. Berricade is lifted]");
            print();
            break;
        else :
            print(f"Comaparison {count} : Value != Vehicle No. : {value}(value)");
            print("[Unregistered vehicle. Berricade remains closed]");
            print();
else :
    print("No documents presents in collection 'customers'.");
