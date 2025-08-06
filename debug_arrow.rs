use std::fs::File;
use std::path::PathBuf;
use arrow::ipc::reader::FileReader as ArrowFileReader;

fn main() {
    let file_path = PathBuf::from("data/test_small.feather");
    println!("Testing Arrow file: {:?}", file_path);
    
    match File::open(&file_path) {
        Ok(file) => {
            println!("File opened successfully");
            match ArrowFileReader::try_new(file, None) {
                Ok(reader) => {
                    println!("Arrow reader created successfully");
                    let schema = reader.schema();
                    println!("Schema: {:?}", schema);
                    
                    let mut batch_count = 0;
                    for batch_result in reader {
                        match batch_result {
                            Ok(batch) => {
                                batch_count += 1;
                                println!("Batch {}: {} rows, {} columns", batch_count, batch.num_rows(), batch.num_columns());
                            },
                            Err(e) => {
                                println!("Error reading batch: {:?}", e);
                            }
                        }
                    }
                },
                Err(e) => {
                    println!("Error creating Arrow reader: {:?}", e);
                }
            }
        },
        Err(e) => {
            println!("Error opening file: {:?}", e);
        }
    }
}
