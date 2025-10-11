# train.py

import tensorflow as tf
import os
import json
import argparse

# --- Step 1: Define a function to create and train an improved model ---
def train_model(data_path, model_name, num_classes, image_size=(224, 224), initial_epochs=10, fine_tune_epochs=20):
    """
    Loads data, adds augmentation, builds a transfer learning model,
    trains it using a two-stage fine-tuning process, and saves the best version.
    """
    print(f"--- Starting training for {model_name} ---")

    # --- Step 2: Load and Prepare the Data ---
    print("Loading and preparing data...")
    # Using a batch size of 32 is a good default
    batch_size = 32
    
    train_dataset = tf.keras.utils.image_dataset_from_directory(
        data_path,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=image_size,
        batch_size=batch_size
    )

    validation_dataset = tf.keras.utils.image_dataset_from_directory(
        data_path,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=image_size,
        batch_size=batch_size
    )

    class_names = train_dataset.class_names
    print(f"Found classes: {class_names}")

    # --- Step 3: Create a Data Augmentation Layer ---
    # This is a key improvement to prevent overfitting and improve accuracy.
    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip('horizontal'),
        tf.keras.layers.RandomRotation(0.2),
        tf.keras.layers.RandomZoom(0.2),
    ])

    # Apply augmentation ONLY to the training dataset
    train_dataset = train_dataset.map(lambda x, y: (data_augmentation(x, training=True), y))

    # Configure datasets for performance
    AUTOTUNE = tf.data.AUTOTUNE
    train_dataset = train_dataset.prefetch(buffer_size=AUTOTUNE)
    validation_dataset = validation_dataset.prefetch(buffer_size=AUTOTUNE)

    # --- Step 4: Build the Model with a Pre-trained Base ---
    print("Building model with transfer learning...")
    
    # Load the base ResNet50 model
    base_model = tf.keras.applications.ResNet50(input_shape=(image_size[0], image_size[1], 3),
                                              include_top=False,
                                              weights='imagenet')

    # Freeze the base model initially
    base_model.trainable = False

    # Create our new model on top
    inputs = tf.keras.Input(shape=(image_size[0], image_size[1], 3))
    # We add a rescaling layer to normalize pixel values to the range [0, 1]
    x = tf.keras.applications.resnet50.preprocess_input(inputs) 
    x = base_model(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.2)(x) # Dropout layer to further prevent overfitting
    outputs = tf.keras.layers.Dense(num_classes, activation='softmax')(x)
    model = tf.keras.Model(inputs, outputs)

    # Compile the model for the first stage of training
    model.compile(optimizer=tf.keras.optimizers.Adam(),
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(),
                  metrics=['accuracy'])
    
    print("--- Stage 1: Training the top layer ---")
    history = model.fit(train_dataset,
                        epochs=initial_epochs,
                        validation_data=validation_dataset)

    # --- Step 5: Fine-Tune the Model ---
    # Unfreeze some layers of the base model to adapt them to our specific dataset.
    print("\n--- Stage 2: Fine-tuning the model ---")
    base_model.trainable = True

    # We'll only unfreeze and train the top layers. The early layers learned
    # very general features (like edges and colors) that are still useful.
    # Let's unfreeze from the 143rd layer onwards.
    fine_tune_at = 143 
    for layer in base_model.layers[:fine_tune_at]:
        layer.trainable = False

    # Re-compile the model with a much lower learning rate for fine-tuning.
    # This is crucial to avoid destroying the learned weights.
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(),
                  metrics=['accuracy'])

    # --- Step 6: Add Callbacks and Continue Training ---
    # Create the main 'model' directory if it doesn't exist
    model_dir = f'../model/{model_name}'
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    # ModelCheckpoint saves the best model based on validation accuracy
    checkpoint_path = f'{model_dir}/{model_name}_best.h5'
    model_checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_path,
        save_weights_only=False,
        monitor='val_accuracy',
        mode='max',
        save_best_only=True)

    # EarlyStopping stops training if the model doesn't improve for 5 epochs
    early_stopping_callback = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True)

    print(f"Continuing training for up to {fine_tune_epochs} more epochs...")
    total_epochs = initial_epochs + fine_tune_epochs
    
    history_fine = model.fit(train_dataset,
                             epochs=total_epochs,
                             initial_epoch=history.epoch[-1], # Continue from where we left off
                             validation_data=validation_dataset,
                             callbacks=[model_checkpoint_callback, early_stopping_callback])

    # --- Step 7: Save the Metrics ---
    # Note: We are saving metrics from the best model found during fine-tuning.
    # The EarlyStopping callback with `restore_best_weights=True` ensures our `model`
    # object has the weights from the best epoch.
    val_acc = max(history_fine.history['val_accuracy'])
    val_loss = min(history_fine.history['val_loss'])
    
    # Find the corresponding training metrics from the same epoch
    best_epoch_index = history_fine.history['val_accuracy'].index(val_acc)
    train_acc = history_fine.history['accuracy'][best_epoch_index]
    train_loss = history_fine.history['loss'][best_epoch_index]

    metrics = {
        'best_validation_accuracy': val_acc,
        'best_validation_loss': val_loss,
        'training_accuracy_at_best_epoch': train_acc,
        'training_loss_at_best_epoch': train_loss,
        'class_names': class_names
    }

    with open(f'{model_dir}/metrics.json', 'w') as f:
        json.dump(metrics, f, indent=4)
        
    print(f"\nTraining complete! Best model saved to {checkpoint_path}")
    print(f"Metrics for the best model saved to {model_dir}/metrics.json")
    print("-" * 20)

# --- Main part of the script ---
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train image classification models with fine-tuning.")
    parser.add_argument('model_type', type=str, choices=['paddy', 'tea', 'all'],
                        help="The type of model to train: 'paddy', 'tea', or 'all'.")
    args = parser.parse_args()

    # --- IMPORTANT: Update these paths to match your folder structure ---
    PADDY_DATA_PATH = 'E:/LeafLens_Project/data/paddy-disease-classification/train_images'
    TEA_DATA_PATH = 'E:/LeafLens_Project/data/tea sickness dataset'
    
    if args.model_type == 'paddy' or args.model_type == 'all':
        if os.path.exists(PADDY_DATA_PATH):
            num_paddy_classes = len(os.listdir(PADDY_DATA_PATH))
            train_model(data_path=PADDY_DATA_PATH, model_name='paddy_model', num_classes=num_paddy_classes)
        else:
            print(f"WARNING: Paddy data path not found at {PADDY_DATA_PATH}. Skipping paddy model training.")
            
    if args.model_type == 'tea' or args.model_type == 'all':
        if os.path.exists(TEA_DATA_PATH):
            num_tea_classes = len(os.listdir(TEA_DATA_PATH))
            train_model(data_path=TEA_DATA_PATH, model_name='tea_model', num_classes=num_tea_classes)
        else:
            print(f"WARNING: Tea data path not found at {TEA_DATA_PATH}. Skipping tea model training.")

    print("All training tasks complete!")