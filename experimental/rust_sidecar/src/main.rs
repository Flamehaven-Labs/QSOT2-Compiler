use std::fs::File;
use std::io::Write;
use turbovec::TurboQuantIndex;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct TestData {
    dim: usize,
    domain_embeddings: Vec<Vec<f32>>,
    query_embedding: Vec<f32>,
    exact_similarities: Vec<f32>,
}

#[derive(Serialize)]
struct VerifyResult {
    verdict: String,
    turbovec_scores: Vec<f32>,
    turbovec_indices: Vec<i64>,
    max_error: f32,
    checks: serde_json::Value,
}

fn main() {
    // 1. Load test data
    let test_data_path = "../test_vectors.json";
    let file = File::open(test_data_path).expect("Failed to open test_vectors.json");
    let test_data: TestData = serde_json::from_reader(file).expect("Failed to parse test_vectors.json");
    
    let dim = test_data.dim;
    let n_vectors = test_data.domain_embeddings.len();
    
    // 2. Initialize TurboQuantIndex
    // Use 4-bit width.
    let mut index = TurboQuantIndex::new(dim, 4).expect("Failed to construct TurboQuantIndex");
    
    // Flatten domain embeddings
    let mut flat_domains = Vec::new();
    for v in &test_data.domain_embeddings {
        flat_domains.extend_from_slice(v);
    }
    
    // Ingest into turbovec
    index.add(&flat_domains);
    
    // 3. Search using the query
    let results = index.search(&test_data.query_embedding, n_vectors);
    
    // 4. Compare similarities
    let mut max_err = 0.0f32;
    let tv_scores = &results.scores;
    let tv_indices = &results.indices;
    
    // Check matching indices and compute differences
    for i in 0..n_vectors {
        let idx = tv_indices[i] as usize;
        let tv_score = tv_scores[i];
        let exact_score = test_data.exact_similarities[idx];
        let err = (tv_score - exact_score).abs();
        if err > max_err {
            max_err = err;
        }
    }
    
    // Since TurboQuant quantizes vectors, some error is expected.
    // However, with 4-bit quantization, the error should be within a small threshold (e.g., < 0.15).
    let error_within_bounds = max_err < 0.15;
    
    let checks = serde_json::json!({
        "turbovec_ingested_correct_count": index.len() == n_vectors,
        "turbovec_returned_all_results": tv_scores.len() == n_vectors,
        "turbovec_quantization_error_within_bounds": error_within_bounds,
    });
    
    let passed = index.len() == n_vectors && tv_scores.len() == n_vectors && error_within_bounds;
    
    let result = VerifyResult {
        verdict: if passed { "PASS".to_string() } else { "FAIL".to_string() },
        turbovec_scores: tv_scores.to_vec(),
        turbovec_indices: tv_indices.to_vec(),
        max_error: max_err,
        checks,
    };
    
    let result_json = serde_json::to_string_pretty(&result).unwrap();
    let mut out_file = File::create("../rust_verify_result.json").expect("Failed to create rust_verify_result.json");
    out_file.write_all(result_json.as_bytes()).unwrap();
    
    println!("Rust verification finished with verdict: {}", result.verdict);
}
