// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ImageVerificationSystem {
    address private owner;
    bool private paused;
    mapping(address => bool) private authorizedUsers;
    
    // Image features struct
    struct ImageFeatures {
        uint256 timestamp;
        address uploader;
        bool isVerified;
        string deepfakeLabel;
        uint256 deepfakeConfidence;
        bool exists;
    }
    
    // Mapping from SHA256 hash to image features
    mapping(string => ImageFeatures) private images;
    
    // Array to store all image hashes for iteration
    string[] private imageHashes;
    
    // Events
    event ImageFeaturesStored(string sha256Hash, uint256 timestamp, address uploader);
    event ImageFeaturesUpdated(string sha256Hash, uint256 timestamp);
    event ImageDeleted(string sha256Hash);
    event ImageVerificationStatusChanged(string sha256Hash, bool isVerified);
    event AuthorizedUserAdded(address user);
    event AuthorizedUserRemoved(address user);
    event ContractPaused(address by);
    event ContractUnpaused(address by);
    
    // Constructor
    constructor() {
        owner = msg.sender;
        authorizedUsers[msg.sender] = true;
        paused = false;
    }
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can call this function");
        _;
    }
    
    modifier onlyAuthorized() {
        require(authorizedUsers[msg.sender], "Caller is not authorized");
        _;
    }
    
    modifier whenNotPaused() {
        require(!paused, "Contract is paused");
        _;
    }
    
    // Owner functions
    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0), "New owner cannot be the zero address");
        owner = newOwner;
    }
    
    function addAuthorizedUser(address user) public onlyOwner {
        authorizedUsers[user] = true;
        emit AuthorizedUserAdded(user);
    }
    
    function removeAuthorizedUser(address user) public onlyOwner {
        require(user != owner, "Cannot remove owner from authorized users");
        authorizedUsers[user] = false;
        emit AuthorizedUserRemoved(user);
    }
    
    function pauseContract() public onlyOwner {
        paused = true;
        emit ContractPaused(msg.sender);
    }
    
    function unpauseContract() public onlyOwner {
        paused = false;
        emit ContractUnpaused(msg.sender);
    }
    
    // Main functions
    function storeImageFeatures(
        string memory sha256Hash,
        string memory deepfakeLabel,
        uint256 deepfakeConfidence
    ) public onlyAuthorized whenNotPaused {
        require(!images[sha256Hash].exists, "Image with this hash already exists");
        
        images[sha256Hash] = ImageFeatures({
            timestamp: block.timestamp,
            uploader: msg.sender,
            isVerified: false,
            deepfakeLabel: deepfakeLabel,
            deepfakeConfidence: deepfakeConfidence,
            exists: true
        });
        
        imageHashes.push(sha256Hash);
        
        emit ImageFeaturesStored(sha256Hash, block.timestamp, msg.sender);
    }
    
    function updateImageFeatures(
        string memory sha256Hash,
        string memory deepfakeLabel,
        uint256 deepfakeConfidence
    ) public onlyAuthorized whenNotPaused {
        require(images[sha256Hash].exists, "Image with this hash does not exist");
        images[sha256Hash].deepfakeLabel = deepfakeLabel;
        images[sha256Hash].deepfakeConfidence = deepfakeConfidence;
        images[sha256Hash].timestamp = block.timestamp;
        
        emit ImageFeaturesUpdated(sha256Hash, block.timestamp);
    }
    
    function deleteImageFeatures(string memory sha256Hash) public onlyAuthorized whenNotPaused {
        require(images[sha256Hash].exists, "Image with this hash does not exist");
        
        // Find the index of the hash in the array
        uint256 index = 0;
        bool found = false;
        
        for (uint256 i = 0; i < imageHashes.length; i++) {
            if (keccak256(bytes(imageHashes[i])) == keccak256(bytes(sha256Hash))) {
                index = i;
                found = true;
                break;
            }
        }
        
        if (found) {
            // Move the last element to the position of the element to delete
            if (index < imageHashes.length - 1) {
                imageHashes[index] = imageHashes[imageHashes.length - 1];
            }
            
            // Remove the last element
            imageHashes.pop();
        }
        
        // Delete the image from the mapping
        delete images[sha256Hash];
        
        emit ImageDeleted(sha256Hash);
    }
    
    function verifyImage(string memory sha256Hash, bool verified) public onlyAuthorized whenNotPaused {
        require(images[sha256Hash].exists, "Image with this hash does not exist");
        
        images[sha256Hash].isVerified = verified;
        
        emit ImageVerificationStatusChanged(sha256Hash, verified);
    }
    
    // View functions
    function getImageFeatures(string memory sha256Hash) public view returns (
        uint256 timestamp,
        address uploader,
        bool isVerified,
        string memory deepfakeLabel,
        uint256 deepfakeConfidence
    ) {
        require(images[sha256Hash].exists, "Image with this hash does not exist");
        
        ImageFeatures memory img = images[sha256Hash];
        
        return (
            img.timestamp,
            img.uploader,
            img.isVerified,
            img.deepfakeLabel,
            img.deepfakeConfidence
        );
    }
    
    function imageExists(string memory sha256Hash) public view returns (bool) {
        return images[sha256Hash].exists;
    }
    
    function getImageCount() public view returns (uint256) {
        return imageHashes.length;
    }
    
    function getImageHashesPaginated(uint256 start, uint256 limit) public view returns (string[] memory) {
        require(start < imageHashes.length, "Start index out of bounds");
        
        uint256 end = start + limit;
        if (end > imageHashes.length) {
            end = imageHashes.length;
        }
        
        uint256 resultLength = end - start;
        string[] memory result = new string[](resultLength);
        
        for (uint256 i = 0; i < resultLength; i++) {
            result[i] = imageHashes[start + i];
        }
        
        return result;
    }
    
    function isAuthorized(address user) public view returns (bool) {
        return authorizedUsers[user];
    }
    
    function isPaused() public view returns (bool) {
        return paused;
    }
    
}