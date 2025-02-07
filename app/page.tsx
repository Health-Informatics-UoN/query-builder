"use client";

import React, { useState } from "react";
import { DataTable } from "./data-table";
import { columns } from "./columns";
import { useGlobalState } from "@/lib/GlobalStateContext";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import GenerateQuery from "@/components/QueryBuilder";
import { Blocks } from "lucide-react";
import { COSD_table, SACT_table } from "@/lib/data";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Tooltips } from "@/components/Tooltips";
import { Condition } from "@/components/QueryBuilder";
import { HowItWork } from "@/components/HowItWork";

const Page: React.FC = () => {
  const [SACT_conditions, setConditionsSACT] = useState<Condition[]>([]);
  const [COSD_conditions, setConditionsCOSD] = useState<Condition[]>([]);

  // TODO: seperate lgics for each table
  const handleAddCondition = (
    column_name: string,
    operator: string,
    value: string,
    reason: string,
    table: string
  ) => {
    if (table == SACT_table.table) {
      setConditionsSACT((prevConditions) => [
        ...prevConditions,
        {
          column_name: column_name,
          operator: operator,
          value: value,
          reason: reason,
        },
      ]);
    } else if (table == COSD_table.table) {
      setConditionsCOSD((prevConditions) => [
        ...prevConditions,
        {
          column_name: column_name,
          operator: operator,
          value: value,
          reason: reason,
        },
      ]);
    }
  };

  const handleRemoveCondition = (index: number, table: string) => {
    if (table == SACT_table.table) {
      setConditionsSACT((prevConditions) =>
        prevConditions.filter((_, i) => i !== index)
      );
    } else if (table == COSD_table.table) {
    }
    setConditionsCOSD((prevConditions) =>
      prevConditions.filter((_, i) => i !== index)
    );
  };

  return (
    <div className="container mx-24 my-5">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-xl font-extrabold text-blue-500 flex items-center">
          Query Buider <Blocks className="ml-2" />
        </h1>
        <Link href="/upload">
          <Button disabled>Upload CSV</Button>
        </Link>
      </div>

      <div>
        <Tabs defaultValue={SACT_table.table}>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-semibold flex">
              Available Table{" "}
              <Tooltips content="Tables that available inside Research View" />
            </h1>
            <TabsList className="">
              <a className="h-full">
                <TabsTrigger value={SACT_table.table}>
                  {SACT_table.table} ({SACT_table.columns.length}){" "}
                  <Tooltips
                    content={`This table has ${SACT_table.columns.length} columns`}
                  />
                </TabsTrigger>
              </a>
              <a className="h-full">
                <TabsTrigger value={COSD_table.table}>
                  {COSD_table.table} ({COSD_table.columns.length}){" "}
                  <Tooltips
                    content={`This table has ${COSD_table.columns.length} columns`}
                  />
                </TabsTrigger>
              </a>
            </TabsList>
          </div>
          <TabsContent value={SACT_table.table}>
            <div className="flex gap-10 justify-between">
              <DataTable
                columns={columns(handleAddCondition)}
                data={SACT_table.columns}
              />
              {/* TODO: add filter column name to search */}
              {SACT_conditions.length > 0 ? (
                <GenerateQuery
                  table={SACT_table.table}
                  conditions={SACT_conditions}
                  onRemoveCondition={handleRemoveCondition}
                />
              ) : (
                <HowItWork />
              )}
            </div>
          </TabsContent>
          <TabsContent value={COSD_table.table}>
            <div className="flex gap-10 justify-between">
              <DataTable
                columns={columns(handleAddCondition)}
                data={COSD_table.columns}
              />
              {COSD_conditions.length > 0 ? (
                <GenerateQuery
                  table={COSD_table.table}
                  conditions={COSD_conditions}
                  onRemoveCondition={handleRemoveCondition}
                />
              ) : (
                <HowItWork />
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Page;
