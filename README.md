<center>
    <img src="https://erwachens.cn/blogimage/images/Avalon/08377ba11f283e0fd3af06127c3e26c.png" width=800 alt="cognitiveclass.ai logo"  />
</center>
# DeepFake Detection System with Blockchain Verification

This README will guide you through the setup and running of the DeepFake Detection System, a Django-React application that uses blockchain technology for verification of images.

## Project Overview

This system allows users to:
- Upload images for DeepFake detection
- Store detection results and image features on the blockchain
- Verify the authenticity of images

## Technology Stack

- **Backend**: Django with Django REST Framework
- **Frontend**: React
- **Database**: PostgreSQL
- **Blockchain**: Ethereum (using Ganache for local development)
- **Wallet**: MetaMask
- **Smart Contract Deployment**: Remix IDE

## Prerequisites

Before starting, make sure you have the following installed:

- Python 3.8+ and pip
- Node.js and npm
- PostgreSQL
- Ganache (desktop version)
- MetaMask browser extension
- Git (optional for cloning the repository)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Set Up the Backend

#### Create a Virtual Environment

```bash
# Create and activate virtual environment
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the project root directory (where `manage.py` is located):

```
# Database Configuration
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Blockchain Configuration
BLOCKCHAIN_RPC=http://127.0.0.1:7545
BLOCKCHAIN_PRIVATE_KEY=your_private_key_from_metamask
CONTRACT_ADDRESS=your_deployed_contract_address
SECRET_KEY=your_django_secret_key
```

#### Create the Database

```bash
# Access PostgreSQL
psql -U postgres

# In PostgreSQL shell
CREATE DATABASE your_db_name;
\q
```

#### Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

#### Create a Superuser

```bash
python manage.py createsuperuser
```

### 3. Set Up Ganache and MetaMask

#### Configure Ganache

1. Launch Ganache desktop application
2. Create a new workspace
3. Configure the server to run on port 7545 (http://127.0.0.1:7545)
4. Note down the mnemonic phrase for MetaMask import

#### Configure MetaMask

1. Install MetaMask browser extension
2. Set up a new account or import an existing one using the Ganache mnemonic
3. Connect MetaMask to Ganache:
   - Click on the network dropdown in MetaMask
   - Select "Add Network"
   - Fill in the following details:
     - Network Name: Ganache
     - New RPC URL: http://127.0.0.1:7545
     - Chain ID: 1337
     - Currency Symbol: ETH
4. Copy your private key from MetaMask:
   - Click on the account icon
   - Click on the three dots
   - Select "Account details"
   - Click "Export Private Key"
   - Enter your password
   - Copy the private key and add it to your `.env` file

### 4. Deploy Smart Contract

1. Open Remix IDE (https://remix.ethereum.org/)
2. Create a new file with the smart contract code (based on the ABI in `blockchain_service.py`)
3. Compile the contract
4. In the "Deploy & Run Transactions" tab:
   - Set the environment to "Injected Web3" (ensure MetaMask is connected to Ganache)
   - Deploy the contract
5. After deployment, copy the contract address and add it to your `.env` file

### 5. Run the Backend Server

```bash
python manage.py runserver
```

The server will start at http://127.0.0.1:8000/

### 6. Run the Frontend (if separate from this repo)

Navigate to your frontend React project directory and run:

```bash
npm install
npm start
```

## Testing the Application

1. Open your browser and navigate to http://localhost:3000 (for the React frontend) or http://127.0.0.1:8000/admin (for the Django admin panel)
2. Log in with the superuser credentials created earlier
3. Upload an image for DeepFake detection
4. The system will process the image, detect potential DeepFakes, and store the results on the blockchain
5. You can verify the blockchain transactions in Ganache

## API Endpoints

- `POST /api/auth/register/`: Register a new user
- `POST /api/auth/login/`: Log in and obtain JWT token
- `POST /api/images/upload/`: Upload a new image for detection
- `GET /api/images/`: List all images
- `GET /api/images/<id>/`: Get details of a specific image
- Check `urls.py` files for additional endpoints

## Troubleshooting

### Blockchain Connection Issues

If you encounter issues connecting to the blockchain:

1. Ensure Ganache is running and accessible at http://127.0.0.1:7545
2. Verify your MetaMask is connected to the Ganache network
3. Check that the contract address and private key in the `.env` file are correct
4. Review the logs in the `logs` directory

### Database Connection Issues

If you have database connection problems:

1. Verify PostgreSQL is running
2. Check your database credentials in the `.env` file
3. Ensure the database exists and is accessible

## Project Structure

- `django_backend/`: Main Django project directory
- `apps/`: Contains Django applications
  - `users/`: User authentication and management
  - `images/`: Image upload and DeepFake detection
- `blockchain_service.py`: Handles blockchain interactions
- `settings.py`: Django project settings

## Additional Notes

- This is a development setup. For production, additional security measures should be implemented.
- The smart contract should be audited before deploying to a public blockchain.
- Make sure to keep your private keys secure and never commit them to version control.


## Contact
ljs282356@gmail.com





=======
# Honour
>>>>>>> c7e760e0547c0df5a0cb8ef872e2e5b95d21d2ed
