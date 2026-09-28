-- BRANCHES
INSERT INTO branches (name, location_region, capacity, supervisor_id) VALUES
('Tampa Branch', 'Southeast', 10, 1),
('Raleigh Branch', 'Southeast', 8, 2);


-- TECHNICIANS
INSERT INTO technicians (name, branch_id) VALUES
('Alex Carter', 1),
('Jordan Lee', 1),
('Taylor Morgan', 2);


-- ATMS
INSERT INTO atms (serial_number, model, status, cash_level, branch_id) VALUES
('ATM-001', 'NCR-100', 'Operational', 15.00, 1),
('ATM-002', 'NCR-100', 'Operational', 75.00, 1),
('ATM-003', 'Diebold-200', 'Maintenance', 40.00, 1),
('ATM-004', 'Diebold-200', 'Operational', 10.00, 2),
('ATM-005', 'NCR-100', 'Maintenance', 55.00, 2);


-- SERVICE CALLS
INSERT INTO service_calls
(title, priority, status, atm_id, technician_id) VALUES
('Refill ATM-001', 'Critical', 'Pending', 1, 1),
('Repair ATM-003', 'Medium', 'In-Progress', 3, 2),
('Inspect ATM-004', 'Low', 'Completed', 4, 3),
('Repair ATM-005', 'Critical', 'Failed', 5, 1);


-- DIAGNOSTIC REPORTS
INSERT INTO diagnostic_reports
(service_call_id, file_url, notes) VALUES
(2, 'https://example.com/report-1.pdf', 'ATM requires maintenance inspection.'),
(3, 'https://example.com/report-2.pdf', 'Inspection completed successfully.'),
(4, 'https://example.com/report-3.pdf', 'Repair attempt failed.');