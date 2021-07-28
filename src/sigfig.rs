use core::str;

// The general logic and return values in this file were learned from the GNU R package pillar in the sigfig.R file.
// A special thanks to the great code quality from Hadley Wickham, Jim Hester, and krlmlr
//
// Format numbers in decimal notation
//
// This formatting system is designed to make it as easy as possible to
// compare columns of numbers.
//
// DecimalSplitsList
//  val: f64, - the given float
//  sigfig: i64, - the given sigfigs (default of 3)
//  neg: bool, - Is a negative needed
//  lhs: String, - Left-hand-side of decimal string
//  rhs: f64, - Right-hand-side budget after spending the lhs digits
//  dec: bool, - should the decimal be included in the print
//
//
//
//                                                                lhs == 0.0
//                                   True                            │                            False            100.0
//                    0.001        ┌─────────────────────────────────┴──────────────────────────────────┐          123.450
//                   -0.12345      │                                                                    │          123456.0
//                   -0.01         │                                                       1 +log10(lhs) >= sigfig
//                                 │                          True                                      │               False
//          n = ((floor(log10(abs(x))) + 1 - sigfig)          ┌─────────────────────────────────────────┴────────────────────┐
//          r =(10^n) * round(x / (10^n))                     │                                                              │
//          return r                                     rhs > 0.0                                                     has negative
//                                 True                       │          False                       True                    │              False
//                                 ┌──────────────────────────┴───────────────┐                         ┌────────────────────┴──────────────┐
//                                 │                                          │                         │                                   │
//                           has negative                                 has negative               concatonate:                     concatonate:
//                                 │                                          │                      (-)                              (lhs)
//                     ┌───────────┴─────────────┐                 ┌──────────┴─────────┐            (lhs)                            (point)
//                     │                         │                 │                    │            (point)                          + sigfig - log10(lhs) from rhs
//                     │                         │                                                   + sigfig - log10(lhs) from rhs
//                     │                         │              concatonate:    concatonate:         (-12.345 -> -12.3)               (12.345 ->  12.3)
//                     │                         │              (-)             (lhs)
//                     │                         │              (lhs)
//                     │                         │                              (1234.0 -> 1234)
//                                                         (-1234.0 -> -1234)
//            concatonate:           concatonate:
//            (-)                    (lhs)
//            (lhs)                  (point)
//            (point)
//            (-123.45 -> -123.)   (1234.50 -> 1234.)
//
//

struct DecimalSplits {
    val: f64,
    sigfig: i64,
}

impl DecimalSplits {
    fn value(&self) -> f64 {
        self.val
    }
    fn sig_fig(&self) -> i64 {
        self.sigfig
    }
    fn neg(&self) -> bool {
        is_neg(self.val)
    }
    fn lhs(&self) -> f64 {
        get_lhs(self.val)
    }
    fn rhs(&self) -> f64 {
        get_rhs(self.val)
    }
    fn dec(&self) -> bool {
        is_decimal(self.val)
    }
    fn final_string(&self) -> String {
        get_final_string(
            self.value(),
            self.lhs(),
            self.rhs(),
            self.neg(),
            self.sig_fig(),
        )
    }
    fn sigfig_index_lhs_or_rhs(&self) -> Option<bool> {
        sigfig_index_lhs_or_rhs(self.final_string(), self.sig_fig())
    }
    fn sigfig_index_from(&self) -> Option<usize> {
        sigfig_index_from(self.final_string(), self.sig_fig())
    }
    fn sigfig_index_to(&self) -> Option<usize> {
        sigfig_index_to(self.final_string(), self.sig_fig())
    }
}

#[derive(Debug)]
struct DecimalSplitsList {
    val: f64,
    sigfig: i64,
    neg: bool,
    lhs: f64,
    rhs: f64,
    dec: bool,
    final_string: String,
    sigfig_index_lhs_or_rhs: Option<bool>, // lhs => True; rhs => False
    sigfig_index_from: Option<usize>,
    sigfig_index_to: Option<usize>,
}

fn is_neg(x: f64) -> bool {
    let r: bool = x < 0.0;
    r
}
fn get_lhs(x: f64) -> f64 {
    let r: f64 = x.trunc();
    r.abs()
}
fn get_rhs(x: f64) -> f64 {
    let xint = x.trunc();
    let frac = x - xint;
    frac.abs()
}
fn is_decimal(x: f64) -> bool {
    let r: f64 = x.trunc() as f64;
    let l = x / r;
    l > 1.0
}
fn get_final_string(x: f64, lhs: f64, rhs: f64, neg: bool, sigfig: i64) -> String {
    if lhs == 0.0 {
        //n = ((floor(log10(abs(x))) + 1 - sigfig)
        //r =(10^n) * round(x / (10^n))
        let n = x.abs().log10().floor() + 1.0 - sigfig as f64;
        let r: f64 = 10f64.powf(n) * ((x / 10f64.powf(n)).round());
        let tmp_string = r.to_string();
        if tmp_string.len() > 13 {
            // 13 is arbitraty. There may be a more general solution here!
            // Problem: debug val: 0.0001 => final_string: "0.00009999999999999999"
            let w = (x.abs().log10().floor()).abs() as usize;
            let fstring = format!("{:.w$}", r, w = w);
            fstring
        } else {
            tmp_string
        }
    } else {
        if lhs.log10() + 1.0 >= sigfig as f64 {
            if rhs > 0.0 {
                if neg == true {
                    //concatonate:
                    //(-)
                    //(lhs)
                    //(point)
                    //(-123.45 -> -123.)
                    let total = lhs + rhs;
                    let total_string = total.to_string();
                    let total_clone = total_string.clone();
                    let split = total_clone.split(".");
                    let vec: Vec<&str> = split.collect();
                    let len_to_take = vec[0].len() + 1; // lhs + point
                    let pos_string = (total_string[..len_to_take]).to_string();
                    let neg_string = "-".to_string();
                    let r = [neg_string, pos_string].join("");
                    r
                } else {
                    //concatonate:
                    //(lhs)
                    //(point)
                    //(123.45 -> 123.)
                    //(123.45 -> 123.)
                    let total = lhs + rhs;
                    let total_string = total.to_string();
                    let total_clone = total_string.clone();
                    let split = total_clone.split(".");
                    let vec: Vec<&str> = split.collect();
                    let len_to_take = vec[0].len() + 1; // lhs + point
                    let r = total_string[..len_to_take].to_string();
                    r
                }
            } else {
                if neg == true {
                    //concatonate:
                    //(-)
                    //(lhs)
                    //(-1234.0 -> -1234)
                    let total = lhs + rhs;
                    let total_string = total.to_string();
                    let total_clone = total_string.clone();
                    let split = total_clone.split(".");
                    let vec: Vec<&str> = split.collect();
                    let len_to_take = vec[0].len(); // lhs
                    let pos_string = (total_string[..len_to_take]).to_string();
                    let neg_string = "-".to_string();
                    let r = [neg_string, pos_string].join("");
                    r
                } else {
                    //concatonate:
                    //(lhs)
                    //(1234.0 -> 1234)
                    //(100.0 -> 100)
                    //let total = lhs + rhs;
                    //let total_string = total.to_string();
                    let total_string = x.to_string();
                    let total_clone = total_string.clone();
                    let split = total_clone.split(".");
                    let vec: Vec<&str> = split.collect();
                    let len_to_take = vec[0].len(); // lhs
                    let r = total_string[..len_to_take].to_string();
                    r
                }
            }
        } else {
            if rhs == 0.0 {
                //concatonate:
                //(lhs)
                //(point)
                //+ sigfig - log10(lhs) from rhs
                let total_string = x.to_string();
                let total_clone = total_string.clone();
                let split = total_clone.split(".");
                let vec: Vec<&str> = split.collect();
                let len_to_take_lhs = vec[0].len(); // point -> +1 to sigfig
                let r = total_string[..len_to_take_lhs].to_string();
                r
            } else {
                if neg == true {
                    //concatonate:
                    //(-)
                    //(lhs)
                    //(point)
                    //+ sigfig - log10(lhs) from rhs
                    //(12.345 -> 12.3)
                    //(1.2345 -> 1.23)
                    // need a rhs arguments here
                    //let total = lhs + rhs;
                    //let total_string = total.to_string();
                    let total_string = x.to_string();
                    let total_clone = total_string.clone();
                    let split = total_clone.split(".");
                    let vec: Vec<&str> = split.collect();
                    let len_to_take_lhs = vec[0].len(); // point -> +1 to sigfig
                    let len_to_take_rhs = ((sigfig + 1) as usize) - len_to_take_lhs;
                    let len_to_take = len_to_take_lhs + len_to_take_rhs + 1; // +1 for the space the neg sign takes
                    let r = total_string[..len_to_take].to_string();
                    r
                } else {
                    //concatonate:
                    //(lhs)
                    //(point)
                    //+ sigfig - log10(lhs) from rhs
                    //(12.345 -> 12.3)
                    //(1.2345 -> 1.23)
                    // need a rhs arguments here
                    //let total = lhs + rhs;
                    //let total_string = total.to_string();
                    let total_string = x.to_string();
                    let total_clone = total_string.clone();
                    let split = total_clone.split(".");
                    let vec: Vec<&str> = split.collect();
                    let len_to_take_lhs = vec[0].len(); // point -> +1 to sigfig
                    let len_to_take_rhs = ((sigfig + 1) as usize) - len_to_take_lhs;
                    let len_to_take = len_to_take_lhs + len_to_take_rhs;
                    let r = total_string[..len_to_take].to_string();
                    r
                }
            }
        }
    }
}
fn sigfig_index_lhs_or_rhs(final_string: String, sigfig: i64) -> Option<bool> {
    // 123456 => {123}456
    // 0.00123 => 0.001{23}
    let total_clone = final_string.clone();
    let split = total_clone.split(".");
    let vec: Vec<&str> = split.collect(); // 12.345 -> ["12", "345"]
    if vec.len() > 1 {
        // if there is a decimal in the string
        let lhs = vec[0].len();
        let rhs = vec[1].len();
        if lhs > sigfig as usize {
            Some(true)
        } else if rhs > sigfig as usize {
            Some(false)
        } else {
            return None;
        }
    } else {
        let lhs = vec[0].len();
        if lhs > sigfig as usize {
            Some(true)
        } else {
            return None;
        }
    }
}
fn sigfig_index_from(final_string: String, sigfig: i64) -> Option<usize> {
    // 123456 => {123}456
    // 0.00123 => 0.001{23}
    // split string on decimal
    // if lhs > sigfig => start = 0
    // else if rhs > sigfig => start = 3 // assuming sigfig = 3
    // else null
    let total_clone = final_string.clone();
    let split = total_clone.split(".");
    let vec: Vec<&str> = split.collect(); // 12.345 -> ["12", "345"]
    if vec.len() > 1 {
        // if there is a decimal in the string
        let lhs = vec[0].len();
        let rhs = vec[1].len();
        if lhs > sigfig as usize {
            Some(0 as usize)
        } else if rhs > sigfig as usize {
            Some(sigfig as usize)
        } else {
            return None;
        }
    } else {
        let lhs = vec[0].len();
        if lhs > sigfig as usize {
            Some(0 as usize)
        } else {
            return None;
        }
    }
}
fn sigfig_index_to(final_string: String, sigfig: i64) -> Option<usize> {
    // 123456 => {123}456
    // 0.00123 => 0.001{23}
    // split string on decimal
    // if lhs > sigfig => end = lhs - sigfig
    // else if rhs > sigfig => end = lhs - sigfig // assuming sigfig = 3
    // else null
    let total_clone = final_string.clone();
    let split = total_clone.split(".");
    let vec: Vec<&str> = split.collect(); // 12.345 -> ["12", "345"]
    if vec.len() > 1 {
        // if there is a decimal in the string
        let lhs = vec[0].len();
        let rhs = vec[1].len();
        if lhs > sigfig as usize {
            let end = lhs - sigfig as usize;
            Some(end)
        } else if rhs > sigfig as usize {
            Some(rhs as usize)
        } else {
            return None;
        }
    } else {
        let lhs = vec[0].len();
        if lhs > sigfig as usize {
            let end = lhs - sigfig as usize;
            Some(end)
        } else {
            return None;
        }
    }
}
fn main() {
    let f12345 = vec![12345.0, 1234.5, 123.45, 12.345, 1.2345, 0.12345];

    for i in 0..f12345.len() {
        let value = f12345[i];
        let x = DecimalSplits {
            val: value,
            sigfig: 3,
        };
        let list = DecimalSplitsList {
            val: x.value(),
            sigfig: x.sig_fig(),
            neg: x.neg(),
            lhs: x.lhs(),
            rhs: x.rhs(),
            dec: x.dec(),
            final_string: x.final_string(),
            sigfig_index_lhs_or_rhs: x.sigfig_index_lhs_or_rhs(),
            sigfig_index_from: x.sigfig_index_from(),
            sigfig_index_to: x.sigfig_index_to(),
        };
        println!("{:#?}", list)
    }
}

#[test]
fn test_f12345() {
    let f12345 = vec![12345.0, 1234.50, 123.45, 12.345, 1.2345, 0.12345];
    let test_sigfig = vec![3, 3, 3, 3, 3, 3];
    let test_neg = vec![false, false, false, false, false, false];
    let test_lhs = vec![12345.0, 1234.0, 123.0, 12.0, 1.0, 0.0];
    let test_rhs = vec![
        0.0,
        0.5,
        0.45000000000000284,
        0.34500000000000064,
        0.23449999999999993,
        0.12345,
    ];
    let test_dec = vec![false, true, true, true, true, true];
    let test_final_string = vec!["12345", "1234.", "123.", "12.3", "1.23", "0.123"];

    for i in 0..f12345.len() {
        let value = f12345[i];
        let x = DecimalSplits {
            val: value,
            sigfig: 3,
        };
        let list = DecimalSplitsList {
            val: x.value(),
            sigfig: x.sig_fig(),
            neg: x.neg(),
            lhs: x.lhs(),
            rhs: x.rhs(),
            dec: x.dec(),
            final_string: x.final_string(),
            sigfig_index_lhs_or_rhs: x.sigfig_index_lhs_or_rhs(),
            sigfig_index_from: x.sigfig_index_from(),
            sigfig_index_to: x.sigfig_index_to(),
        };
        println!("{:#?}", list);
        assert_eq!(list.val, f12345[i]);
        assert_eq!(list.sigfig, test_sigfig[i]);
        assert_eq!(list.neg, test_neg[i]);
        assert_eq!(list.lhs, test_lhs[i]);
        assert_eq!(list.rhs, test_rhs[i]);
        assert_eq!(list.dec, test_dec[i]);
        assert_eq!(list.final_string, test_final_string[i]);
    }

    //    $sigfig
    //    [1] 3
    //    $num
    //    [1] TRUE TRUE TRUE TRUE TRUE TRUE
    //    $neg
    //    [1] FALSE FALSE FALSE FALSE FALSE FALSE
    //    $lhs
    //    [1] "12345" "1234"  "123"   "12"    "1"     "0"
    //    $lhs_zero
    //    [1] FALSE FALSE FALSE FALSE FALSE  TRUE
    //    $rhs
    //    [1] 0.000 0.000 0.000 0.300 0.230 0.123
    //    $rhs_digits
    //    [1]  0 -1  0  1  2  3
    //    $dec
    //    [1] FALSE  TRUE  TRUE  TRUE  TRUE  TRUE
    //    $exp
    //    [1] NA NA NA NA NA NA
    //    $si
    //    [1] FALSE
    //    attr(,"width")
    //    [1] 9
    //    12345
    //     1234.
    //      123.
    //       12.3
    //        1.23
    //        0.123
}

#[test]
fn test_f100() {
    let f100 = vec![100.0, 10.0, 1.0, 0.1, 0.01, 0.001, 0.0001];
    let test_sigfig = vec![3, 3, 3, 3, 3, 3, 3];
    let test_neg = vec![false, false, false, false, false, false, false];
    let test_lhs = vec![100.0, 10.0, 1.0, 0.0, 0.0, 0.0, 0.0];
    let test_rhs = vec![0.0, 0.0, 0.0, 0.1, 0.01, 0.001, 0.0001];
    let test_dec = vec![false, false, false, true, true, true, true];
    let test_final_string = vec!["100", "10", "1", "0.1", "0.01", "0.001", "0.0001"];

    for i in 0..f100.len() {
        let value = f100[i];
        println!("{}", value);
        let x = DecimalSplits {
            val: value,
            sigfig: 3,
        };
        let list = DecimalSplitsList {
            val: x.value(),
            sigfig: x.sig_fig(),
            neg: x.neg(),
            lhs: x.lhs(),
            rhs: x.rhs(),
            dec: x.dec(),
            final_string: x.final_string(),
            sigfig_index_lhs_or_rhs: x.sigfig_index_lhs_or_rhs(),
            sigfig_index_from: x.sigfig_index_from(),
            sigfig_index_to: x.sigfig_index_to(),
        };
        println!("{:#?}", list);
        assert_eq!(list.val, f100[i]);
        assert_eq!(list.sigfig, test_sigfig[i]);
        assert_eq!(list.neg, test_neg[i]);
        assert_eq!(list.lhs, test_lhs[i]);
        assert_eq!(list.rhs, test_rhs[i]);
        assert_eq!(list.dec, test_dec[i]);
        assert_eq!(list.final_string, test_final_string[i]);
        println!("complete!");
    }

    //$sigfig
    //[1] 3
    //$num
    //[1] TRUE TRUE TRUE TRUE TRUE TRUE
    //$neg
    //[1] FALSE FALSE FALSE FALSE FALSE FALSE
    //$lhs
    //[1] "100" "10"  "1"   "0"   "0"   "0"
    //$lhs_zero
    //[1] FALSE FALSE FALSE  TRUE  TRUE  TRUE
    //$rhs
    //[1] 0.000 0.000 0.000 0.100 0.010 0.001
    //$rhs_digits
    //[1] 0 0 0 1 2 3
    //$dec
    //[1] FALSE FALSE FALSE  TRUE  TRUE  TRUE
    //$exp
    //[1] NA NA NA NA NA NA
    //$si
    //[1] FALSE
    //attr(,"width")
    //[1] 7
    //100
    // 10
    //  1
    //  0.1
    //  0.01
    //  0.001
}

#[test]
fn test_fn100() {
    let f100 = vec![-100.0, -10.0, -1.0, -0.1, -0.01, -0.001, -0.0001];
    let test_sigfig = vec![3, 3, 3, 3, 3, 3, 3];
    let test_neg = vec![true, true, true, true, true, true, true];
    let test_lhs = vec![100.0, 10.0, 1.0, 0.0, 0.0, 0.0, 0.0];
    let test_rhs = vec![0.0, 0.0, 0.0, 0.1, 0.01, 0.001, 0.0001];
    let test_dec = vec![false, false, false, true, true, true, true];
    let test_final_string = vec!["-100", "-10", "-1", "-0.1", "-0.01", "-0.001", "-0.0001"];

    for i in 0..f100.len() {
        let value = f100[i];
        println!("{}", value);
        let x = DecimalSplits {
            val: value,
            sigfig: 3,
        };
        let list = DecimalSplitsList {
            val: x.value(),
            sigfig: x.sig_fig(),
            neg: x.neg(),
            lhs: x.lhs(),
            rhs: x.rhs(),
            dec: x.dec(),
            final_string: x.final_string(),
            sigfig_index_lhs_or_rhs: x.sigfig_index_lhs_or_rhs(),
            sigfig_index_from: x.sigfig_index_from(),
            sigfig_index_to: x.sigfig_index_to(),
        };
        println!("{:#?}", list);
        assert_eq!(list.val, f100[i]);
        assert_eq!(list.sigfig, test_sigfig[i]);
        assert_eq!(list.neg, test_neg[i]);
        assert_eq!(list.lhs, test_lhs[i]);
        assert_eq!(list.rhs, test_rhs[i]);
        assert_eq!(list.dec, test_dec[i]);
        assert_eq!(list.final_string, test_final_string[i]);
        println!("complete!");
    }
    //$sigfig
    //[1] 3
    //$num
    //[1] TRUE TRUE TRUE TRUE TRUE TRUE TRUE
    //$neg
    //[1] TRUE TRUE TRUE TRUE TRUE TRUE TRUE
    //$lhs
    //[1] "100" "10"  "1"   "0"   "0"   "0"   "0"
    //$lhs_zero
    //[1] FALSE FALSE FALSE  TRUE  TRUE  TRUE  TRUE
    //$rhs
    //[1] 0e+00 0e+00 0e+00 1e-01 1e-02 1e-03 1e-04
    //$rhs_digits
    //[1] 0 0 0 1 2 3 4
    //$dec
    //[1] FALSE FALSE FALSE  TRUE  TRUE  TRUE  TRUE
    //$exp
    //[1] NA NA NA NA NA NA NA
    //$si
    //[1] FALSE
    //attr(,"width")
    //[1] 9
}

#[test]
fn test_fn12345() {
    let f12345 = vec![-12345.0, -1234.50, -123.45, -12.345, -1.2345, -0.12345];
    let test_sigfig = vec![3, 3, 3, 3, 3, 3];
    let test_neg = vec![true, true, true, true, true, true, true];
    let test_lhs = vec![12345.0, 1234.0, 123.0, 12.0, 1.0, 0.0];
    let test_rhs = vec![
        0.0,
        0.5,
        0.45000000000000284,
        0.34500000000000064,
        0.23449999999999993,
        0.12345,
    ];
    let test_dec = vec![false, true, true, true, true, true];
    let test_final_string = vec!["-12345", "-1234.", "-123.", "-12.3", "-1.23", "-0.123"];

    for i in 0..f12345.len() {
        let value = f12345[i];
        let x = DecimalSplits {
            val: value,
            sigfig: 3,
        };
        let list = DecimalSplitsList {
            val: x.value(),
            sigfig: x.sig_fig(),
            neg: x.neg(),
            lhs: x.lhs(),
            rhs: x.rhs(),
            dec: x.dec(),
            final_string: x.final_string(),
            sigfig_index_lhs_or_rhs: x.sigfig_index_lhs_or_rhs(),
            sigfig_index_from: x.sigfig_index_from(),
            sigfig_index_to: x.sigfig_index_to(),
        };
        println!("{:#?}", list);
        assert_eq!(list.val, f12345[i]);
        assert_eq!(list.sigfig, test_sigfig[i]);
        assert_eq!(list.neg, test_neg[i]);
        assert_eq!(list.lhs, test_lhs[i]);
        assert_eq!(list.rhs, test_rhs[i]);
        assert_eq!(list.dec, test_dec[i]);
        assert_eq!(list.final_string, test_final_string[i]);
    }

    //    $sigfig
    //    [1] 3
    //    $num
    //    [1] TRUE TRUE TRUE TRUE TRUE TRUE
    //    $neg
    //    [1] FALSE FALSE FALSE FALSE FALSE FALSE
    //    $lhs
    //    [1] "12345" "1234"  "123"   "12"    "1"     "0"
    //    $lhs_zero
    //    [1] FALSE FALSE FALSE FALSE FALSE  TRUE
    //    $rhs
    //    [1] 0.000 0.000 0.000 0.300 0.230 0.123
    //    $rhs_digits
    //    [1]  0 -1  0  1  2  3
    //    $dec
    //    [1] FALSE  TRUE  TRUE  TRUE  TRUE  TRUE
    //    $exp
    //    [1] NA NA NA NA NA NA
    //    $si
    //    [1] FALSE
    //    attr(,"width")
    //    [1] 9
    //    12345
    //     1234.
    //      123.
    //       12.3
    //        1.23
    //        0.123
}
